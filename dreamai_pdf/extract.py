# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/01_extract.ipynb.

# %% auto 0
__all__ = ['print_segments', 'text_to_segments', 'load_segs_model', 'load_ems_model', 'write_segments', 'write_embeddings']

# %% ../nbs/01_extract.ipynb 2
from .imports import *
from .core import *


# %% ../nbs/01_extract.ipynb 3
def print_segments(segments: dict, limit: int = 10, width: int = 100):
    for k, v in segments.items():
        print(f"{k}: {len(v)}")
        for s in v[:limit]:
            print("\t", end="")
            pprint(s, width=width)
            print()
        print("-" * width + 4)


def text_to_segments(
    text: Union[str, List[str]],
    segs_model: SetFitModel,
    thresh: float = 0.6,
    classes: List = ["Work Experience", "Education", "Certifications", "Other"],
):
    preds = segs_model.predict(text).detach().cpu().numpy()
    probs = segs_model.predict_proba(text).detach().cpu().numpy().max(1)
    preds[probs < thresh] = 3
    pred_classes = [classes[p] for p in preds]
    segments = {pc: [] for pc in classes}
    for pc, txt in zip(pred_classes, text):
        if txt not in segments[pc]:
            segments[pc].append(txt)
    return segments, pred_classes, probs


def load_segs_model(
    model_name: str = "HamzaFarhan/PDFSegs", device: Union[str, torch.device] = "cpu"
):
    return SetFitModel.from_pretrained(model_name).to(device)


def load_ems_model(
    model_name: str = "HamzaFarhan/PDFSegs", device: Union[str, torch.device] = "cpu"
):
    return SentenceTransformer(model_name, device=device)


def write_segments(segs_model, data_path, output_path="pdf_segments", n_lines=2):
    """
    Extracts text from PDFs and writes segments to JSON files.

    Parameters
    ----------
    segs_model : SetFitModel
        SetFit model for segment classification.
    data_path : Union[str, Path, List[Union[str, Path]]]
        Path to PDFs. Can be a single file, a directory, or a list of files/directories.
    output_path : Union[str, Path]
        Folder to write JSON files. Defaults to 'pdf_segments'.
    n_lines : int
        Number of lines to group together when extracting text from PDFs.
    Returns
    -------
    None
    """
    output_path = Path(output_path)
    os.makedirs(output_path, exist_ok=True)
    pdfs = resolve_data_path(data_path)
    text_dict = extract_text_dict(pdfs, n_lines=n_lines)
    for file in pdfs:
        try:
            pdf_text = text_dict[str(file)]
            (segments,) = text_to_segments(pdf_text, segs_model, thresh=0.6)[0]
            fn = (output_path / Path(file).stem).with_suffix(".json")
            with open(fn, "w") as f:
                json.dump(segments, f, indent=4)
        except Exception as e:
            msg.fail(f"\nCould not write segments for file: {str(file)}", e)
            # print(f"\nCould not write segments for file: {str(file)}\n{e}")


def write_embeddings(
    segs_model, ems_model, data_path, output_path="pdf_ems", n_lines=3
):
    """
    Extracts text from PDFs and writes embeddings to JSON files.

    Parameters
    ----------
    segs_model : SetFitModel
        SetFit model for segment classification.
    ems_model : SentenceTransformer
        SentenceTransformer model for embedding generation.
    data_path : Union[str, Path, List[Union[str, Path]]]
        Path to PDFs. Can be a single file, a directory, or a list of files/directories.
    output_path : Union[str, Path]
        Folder to write JSON files. Defaults to 'pdf_ems'.
    n_lines : int
        Number of lines to group together when extracting text from PDFs.
    Returns
    -------
    None
    """
    os.makedirs(output_path, exist_ok=True)
    seg_ids = {"Work Experience": 1, "Education": 2, "Certifications": 3, "Other": 4}
    pdfs = resolve_data_path(data_path)
    text_dict = extract_text_dict(pdfs, n_lines=n_lines)
    for file in pdfs:
        try:
            fn = Path(file).stem
            pdf_text = text_dict[str(file)]
            ems = ems_model.encode(pdf_text)
            pred_classes = text_to_segments(pdf_text, segs_model)[1]
            for i, data in enumerate(zip(pred_classes, ems)):
                pc, em = data
                seg_id = seg_ids[pc]
                jf = Path(output_path) / f"{fn}_{seg_id}_{i+1}.json"
                em_dict = {"id": fn, "embedding": em.tolist()}
                with open(jf, "w") as f:
                    json.dump(em_dict, f)
        except Exception as e:
            msg.fail(f"\nCould not write embeddings for {str(file)}", e)
            # print(f"\nCould not write embeddings for {str(file)}\n{e}")
