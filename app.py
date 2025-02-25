import time
from pathlib import Path

import gradio as gr
import pymupdf4llm
from gradio_pdf import PDF

from backends import (
    convert_docling,
    convert_marker,
    convert_mineru,
    convert_unstructured,
)
from backends.settings import ENABLE_DEBUG_MODE
from utils import remove_images_from_markdown, trim_pages

TRIMMED_PDF_PATH = Path("/tmp/gradio/trim")
TRIMMED_PDF_PATH.mkdir(exist_ok=True)


def convert_document(path, method, enabled=True):
    if enabled:
        print("Processing file", path, "with method", method)
    else:
        return "", "", []

    # benchmarking
    start = time.time()

    path = trim_pages(path, output_path=TRIMMED_PDF_PATH)
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

    end = time.time()
    print(f"Conversion with {method} took {end - start} seconds")
    return text, remove_images_from_markdown(text), debug_image_paths


def show_tabs(selected_methods):
    visible_tabs = []
    for method in supported_methods:
        visible_tabs.append(gr.update(visible=method in selected_methods))

    return visible_tabs


latex_delimiters = [
    {"left": "$$", "right": "$$", "display": True},
    {"left": "$", "right": "$", "display": False},
]

# startup test (also for loading models the first time)
start_startup = time.time()
test_pdf_path = "/home/tadashi/MinerU/examples/complex_layout.pdf"
supported_methods = ["Docling", "Marker", "Unstructured", "MinerU", "PyMuPDF"]

# print("Warm-up sequence")
# for method in supported_methods:
#     for _ in range(1):
#         convert_document(test_pdf_path, method)
# print("Start up time", time.time() - start_startup, "seconds")

with gr.Blocks(
    theme=gr.themes.Ocean(),
) as demo:
    with open("header.html", "r") as file:
        header = file.read()
    gr.HTML(header)
    output_components = []
    output_tabs = []
    visualization_sub_tabs = []
    first_method = supported_methods[0]

    with gr.Row():
        with gr.Column(variant="panel", scale=5):
            input_file = gr.File(
                label="Upload PDF document",
                file_types=[
                    ".pdf",
                ],
            )
            progress_status = gr.Markdown("", show_label=False, container=False)

        with gr.Column(variant="panel", scale=5):
            with gr.Row():
                methods = gr.Dropdown(
                    supported_methods,
                    label="Conversion methods",
                    value=first_method,
                    multiselect=True,
                )
            with gr.Row():
                visual_checkbox = gr.Checkbox(
                    label="Enable debug visualizations",
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
                for method in supported_methods:
                    with gr.Tab(method, visible=False) as output_tab:
                        with gr.Tabs():
                            with gr.Tab("Markdown rendering"):
                                markdown_render = gr.Markdown(
                                    label="Markdown rendering",
                                    height=900,
                                    show_copy_button=True,
                                    line_breaks=True,
                                    latex_delimiters=latex_delimiters,
                                )
                            with gr.Tab(
                                "Debug visualizations",
                                visible=ENABLE_DEBUG_MODE,
                            ) as visual_sub_tab:
                                debug_images = gr.Gallery(
                                    show_label=False,
                                    container=False,
                                    interactive=False,
                                )
                            with gr.Tab("Raw text"):
                                markdown_text = gr.TextArea(
                                    lines=45, show_label=False, container=False
                                )

                    output_components.extend(
                        [markdown_render, markdown_text, debug_images]
                    )
                    output_tabs.append(output_tab)
                    visualization_sub_tabs.append(visual_sub_tab)

    input_file.change(fn=lambda x: x, inputs=input_file, outputs=pdf_preview)
    click_event = convert_btn.click(
        fn=show_tabs,
        inputs=[methods],
        outputs=output_tabs,
    )
    for idx, method in enumerate(supported_methods):

        def progress_message(selected_methods, method=method):
            selected_methods_indices = [
                idx
                for idx, current_method in enumerate(supported_methods)
                if current_method in selected_methods
            ]
            try:
                current_method_idx = selected_methods_indices.index(
                    supported_methods.index(method)
                )
                msg = (
                    f"Processing ({current_method_idx + 1} / "
                    f"{len(selected_methods)}) **{method}**...\n\n"
                )
            except ValueError:
                msg = gr.update()

            return msg

        def process_method(input_file, selected_methods, method=method):
            if input_file is None:
                raise ValueError("Please upload a PDF file first!")
            return convert_document(
                input_file, method=method, enabled=method in selected_methods
            )

        click_event = click_event.then(
            fn=lambda methods, method=method: progress_message(methods, method),
            inputs=[methods],
            outputs=[progress_status],
        ).then(
            fn=lambda input_file, methods, method=method: process_method(
                input_file, methods, method
            ),
            inputs=[input_file, methods],
            outputs=output_components[idx * 3 : (idx + 1) * 3],
        )

    click_event.then(
        lambda: "All tasks completed.",
        outputs=[progress_status],
    )

    clear_btn.add(
        [
            input_file,
            pdf_preview,
        ]
        + output_components
    )

    visual_checkbox.change(
        fn=lambda state: [gr.update(visible=state)] * len(visualization_sub_tabs),
        inputs=visual_checkbox,
        outputs=visualization_sub_tabs,
    )

    demo.launch(show_error=True)
