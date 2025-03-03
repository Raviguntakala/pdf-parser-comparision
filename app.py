import os
import zipfile
from collections import defaultdict

from utils import patch_unimernet_model, prepare_env_mineru

patch_unimernet_model()  # noqa
prepare_env_mineru()  # noqa


import time
from pathlib import Path

import gradio as gr
import pymupdf4llm
from gradio_pdf import PDF

from backends import (  # convert_zerox,
    SUPPORTED_METHODS,
    SUPPORTED_METHODS_METADATA,
    convert_docling,
    convert_gemini,
    convert_gmft,
    convert_img2table,
    convert_marker,
    convert_mineru,
    convert_sycamore,
    convert_unstructured,
)
from backends.settings import ENABLE_DEBUG_MODE
from utils import remove_images_from_markdown, trim_pages

TRIMMED_PDF_PATH = Path("/tmp/trimmed_input")
TRIMMED_PDF_PATH.mkdir(exist_ok=True)
DO_WARMUP = os.getenv("DO_WARMUP", "True").lower() == "true"


def convert_document(path, method, start_page=0, enabled=True):
    if enabled:
        print("Processing file", path, "with method", method)
    else:
        return "", "", "", []

    # benchmarking
    start = time.time()

    path = trim_pages(
        path,
        output_path=TRIMMED_PDF_PATH,
        start_page=start_page,
    )
    file_name = Path(path).stem
    debug_image_paths = []
    text = "unknown method"

    if method == "Docling":
        text, debug_image_paths = convert_docling(path, file_name)
    elif method == "Marker":
        text, debug_image_paths = convert_marker(path, file_name)
    elif method == "Unstructured":
        text, debug_image_paths = convert_unstructured(path, file_name)
    elif method == "PyMuPDF":
        text = pymupdf4llm.to_markdown(
            path,
            embed_images=True,
        )
    elif method == "MinerU":
        text, debug_image_paths = convert_mineru(path, file_name)
    elif method == "Gemini (API)":
        text, debug_image_paths = convert_gemini(path, file_name)
    elif method == "Sycamore":
        text, debug_image_paths = convert_sycamore(path, file_name)
    # elif method == "Zerox":
    #     text, debug_image_paths = convert_zerox(path, file_name)
    elif method == "Img2Table (table-only)":
        text, debug_image_paths = convert_img2table(path, file_name)
    elif method == "GMFT (table-only)":
        text, debug_image_paths = convert_gmft(path, file_name)
    else:
        raise ValueError(f"Unsupported method: {method}")

    duration = time.time() - start
    duration_message = f"Conversion with {method} took *{duration:.2f} seconds*"
    print(duration_message)
    return (
        duration_message,
        text,
        remove_images_from_markdown(text),
        debug_image_paths,
    )


def to_zip_file(file_path, methods, *output_components):
    markdown_text_dict = dict()
    debug_images_dict = defaultdict(list)
    for idx, method_name in enumerate(SUPPORTED_METHODS):
        if method_name not in methods:
            continue

        markdown_text = output_components[idx * 4 + 2]
        debug_images = output_components[idx * 4 + 3]

        markdown_text_dict[method_name] = markdown_text
        debug_images_dict[method_name] = debug_images

    # create new temp directory using Python's tempfile module
    temp_dir = Path(file_path).parent
    zip_file_path = temp_dir / "output.zip"

    markdown_path = temp_dir / f"{method_name}.md"
    with open(markdown_path, "w") as f:
        f.write(markdown_text)

    # create a zip file in write mode
    with zipfile.ZipFile(zip_file_path, "w", zipfile.ZIP_DEFLATED) as zipf:
        for method_name, markdown_text in markdown_text_dict.items():
            debug_image_paths = debug_images_dict[method_name]

            # write the markdown text to the zip file
            zipf.write(
                markdown_path,
                f"{method_name}/{method_name}.md",
            )
            if debug_image_paths:
                for idx, (debug_image_path, _) in enumerate(debug_image_paths):
                    debug_image_name = Path(debug_image_path).name
                    zipf.write(
                        debug_image_path,
                        f"{method_name}/{debug_image_name}",
                    )

    return gr.update(
        value=str(zip_file_path),
        visible=True,
    )


def show_tabs(selected_methods):
    visible_tabs = []
    for method in SUPPORTED_METHODS:
        visible_tabs.append(gr.update(visible=method in selected_methods))

    return visible_tabs


latex_delimiters = [
    {"left": "$$", "right": "$$", "display": True},
    {"left": "$", "right": "$", "display": False},
]

# startup test (also for loading models the first time)
start_startup = time.time()
WARMUP_PDF_PATH = "examples/table.pdf"

if DO_WARMUP:
    print("Warm-up sequence")
    for method in SUPPORTED_METHODS:
        for _ in range(1):
            convert_document(WARMUP_PDF_PATH, method)
    startup_duration = time.time() - start_startup
    print(f"Total start-up time: {startup_duration:.2f} seconds")

with gr.Blocks(
    theme=gr.themes.Ocean(),
) as demo:
    with open("header.html", "r") as file:
        header = file.read()
    gr.HTML(header)
    output_components = []
    output_tabs = []
    visualization_sub_tabs = []

    with gr.Row():
        with gr.Column(variant="panel", scale=5):
            input_file = gr.File(
                label="Upload PDF document",
                file_types=[
                    ".pdf",
                ],
            )
            with gr.Accordion("Examples:"):
                example_root = os.path.join(os.path.dirname(__file__), "examples")
                gr.Examples(
                    examples=[
                        os.path.join(example_root, _)
                        for _ in os.listdir(example_root)
                        if _.endswith("pdf")
                    ],
                    inputs=input_file,
                )
            progress_status = gr.Markdown("", show_label=False, container=False)
            output_file = gr.File(
                label="Download output",
                interactive=False,
                visible=False,
            )

        with gr.Column(variant="panel", scale=5):
            with gr.Row():
                methods = gr.Dropdown(
                    SUPPORTED_METHODS,
                    label="Conversion methods",
                    value=SUPPORTED_METHODS[:2],
                    multiselect=True,
                )
            with gr.Row():
                with gr.Accordion(
                    "Advanced settings",
                    open=False,
                ):
                    start_page = gr.Number(
                        label=(
                            "Starting page (only max 5 "
                            "consecutive pages are processed)"
                        ),
                        minimum=1,
                        maximum=100,
                        step=1,
                        value=1,
                    )
                    visual_checkbox = gr.Checkbox(
                        label="Enable debug visualization",
                        visible=ENABLE_DEBUG_MODE,
                        value=True,
                    )
            with gr.Row():
                convert_btn = gr.Button("Convert", variant="primary", scale=2)
                clear_btn = gr.ClearButton(value="Clear", scale=1)

    with gr.Row():
        with gr.Column(variant="panel", scale=5):
            pdf_preview = PDF(
                label="PDF preview",
                interactive=False,
                visible=True,
                height=800,
            )

        with gr.Column(variant="panel", scale=5):
            with gr.Tabs():
                for method in SUPPORTED_METHODS:
                    with gr.Tab(method, visible=False) as output_tab:
                        with gr.Tabs():
                            with gr.Tab("Markdown render"):
                                markdown_render = gr.Markdown(
                                    label="Markdown rendering",
                                    height=900,
                                    show_copy_button=True,
                                    line_breaks=True,
                                    latex_delimiters=latex_delimiters,
                                )
                            with gr.Tab("Markdown text"):
                                markdown_text = gr.TextArea(
                                    lines=45, show_label=False, container=False
                                )
                            with gr.Tab(
                                "Debug visualization",
                                visible=ENABLE_DEBUG_MODE,
                            ) as visual_sub_tab:
                                output_description = gr.Markdown(
                                    container=False,
                                    show_label=False,
                                )
                                debug_images = gr.Gallery(
                                    show_label=False,
                                    container=False,
                                    interactive=False,
                                )
                            with gr.Tab("About"):
                                method_metadata = SUPPORTED_METHODS_METADATA[
                                    method
                                ]  # type: ignore
                                method_name = method_metadata["name"]  # type: ignore
                                method_description = method_metadata[
                                    "description"
                                ]  # type: ignore
                                method_url = method_metadata["url"]  # type: ignore
                                method_documentation = method_metadata[
                                    "documentation"
                                ]  # type: ignore
                                gr.Markdown(
                                    value=(
                                        f"# {method_name}\n\n{method_description}\n\n"
                                        + (
                                            f"[[Github repo]]({method_url})    "
                                            if method_url
                                            else ""
                                        )
                                        + f"[[Documentation]]({method_documentation})"
                                    ),
                                    container=False,
                                    show_label=False,
                                )

                    output_components.extend(
                        [
                            output_description,
                            markdown_render,
                            markdown_text,
                            debug_images,
                        ]
                    )
                    output_tabs.append(output_tab)
                    visualization_sub_tabs.append(visual_sub_tab)

    input_file.change(fn=lambda x: x, inputs=input_file, outputs=pdf_preview)
    click_event = convert_btn.click(
        fn=show_tabs,
        inputs=[methods],
        outputs=output_tabs,
    )
    for idx, method in enumerate(SUPPORTED_METHODS):

        def progress_message(selected_methods, method=method):
            selected_methods_indices = [
                idx
                for idx, current_method in enumerate(SUPPORTED_METHODS)
                if current_method in selected_methods
            ]
            try:
                current_method_idx = selected_methods_indices.index(
                    SUPPORTED_METHODS.index(method)
                )
                msg = (
                    f"Processing ({current_method_idx + 1} / "
                    f"{len(selected_methods)}) **{method}**...\n\n"
                )
            except ValueError:
                msg = gr.update()

            return msg

        def process_method(input_file, start_page, selected_methods, method=method):
            if input_file is None:
                raise ValueError("Please upload a PDF file first!")
            return convert_document(
                input_file,
                method=method,
                start_page=start_page - 1,
                enabled=method in selected_methods,
            )

        click_event = click_event.then(
            fn=lambda methods, method=method: progress_message(methods, method),
            inputs=[methods],
            outputs=[progress_status],
        ).then(
            fn=lambda input_file, start_page, methods, method=method: process_method(
                input_file, start_page, methods, method
            ),
            inputs=[input_file, start_page, methods],
            outputs=output_components[idx * 4 : (idx + 1) * 4],
        )

    click_event.then(lambda: "All tasks completed.", outputs=[progress_status],).then(
        fn=to_zip_file,
        inputs=[
            input_file,
            methods,
        ]
        + output_components,
        outputs=[output_file],
    )

    clear_btn.add(
        [
            input_file,
            pdf_preview,
            output_file,
        ]
        + output_components
    )
    clear_btn.click(
        fn=lambda: gr.update(visible=False),
        outputs=[output_file],
    )

    visual_checkbox.change(
        fn=lambda state: [gr.update(visible=state)] * len(visualization_sub_tabs),
        inputs=visual_checkbox,
        outputs=visualization_sub_tabs,
    )

    demo.queue(default_concurrency_limit=2,).launch(
        show_error=True,
        max_file_size="50mb",
    )
