# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/00_core.ipynb.

# %% auto 0
__all__ = ['cid_to_char', 'process_text', 'process_line', 'extract_text', 'extract_text_list', 'extract_text_dict']

# %% ../nbs/00_core.ipynb 2
from .imports import *


# %% ../nbs/00_core.ipynb 3
def cid_to_char(cidx: str):
    try:
        return chr(int(re.findall(r"\(cid\:(\d+)\)", cidx)[0]) + 29)
    except:
        return cidx


def process_text(text: str):
    text = text.strip()
    text = cid_to_char(text)
    text = re.sub("\xa0", " ", text)
    text = re.sub(r"\uf0b7", " ", text)
    text = re.sub(r"\(cid:\d{0,3}\)", " ", text)
    text = re.sub(r"•", "", text)
    text = re.sub(r"●", "", text)
    text = re.sub(r"▪", "", text)
    text = re.sub(r"", "", text)
    text = re.sub(r"➢", "", text)
    text = re.sub(r"\u2b9a", "", text)
    text = re.sub(r"\u201c", "", text)
    text = re.sub(r"\u201d", "", text)
    text = re.sub(r"\u2013", " ", text)
    text = re.sub(r"\u2019", "'", text)
    text = re.sub(r"\u2018", "'", text)
    text = re.sub(r"\u00f4", " ", text)
    text = re.sub(r"\u00f6", "o", text)
    text = re.sub(r"\u00e9", "e", text)
    text = re.sub(r"\u00e8", "e", text)
    text = re.sub(r"\u00e7", " ", text)
    text = re.sub(r"\u00a7", "", text)
    text = re.sub(r"\u00e3", "a", text)
    text = re.sub(r"\uf0a7", "", text)
    text = re.sub(r"\uf076", "", text)
    text = re.sub(r"\u00ad", "", text)
    text = re.sub(r"\u00ab", "", text)
    text = re.sub(r"\u00bb", "", text)
    text = re.sub(r"\uf02d", "", text)
    text = re.sub(r"\uf0fc", "", text)
    text = re.sub(r"\uf06e", "", text)
    text = re.sub(r"\uf07a", "", text)
    text = re.sub(r"\ufb01", "fi", text)
    text = re.sub(r"\ufb00", "ff", text)
    text = re.sub(r"\uf0d8", "", text)
    text = re.sub(r"\u00b7", "", text)
    text = re.sub("\t", " ", text)
    text = re.sub(" +", " ", text)
    return text.strip()


def process_line(txt, n_lines=2):
    txt = process_text(txt)
    if not txt.isspace() and len(txt) > 2:
        if len(txt) > 512:
            nw = 10 * n_lines
            txt = txt.split()
            txt = [" ".join(txt[i : i + nw]) for i in range(0, len(txt), nw)]
        return txt
    return None


def extract_text(file, n_lines=3):
    if Path(file).suffix == ".pdf":
        try:
            pdf = PdfReader(str(file))
            pdf_text = []
            for pn, page in enumerate(pdf.pages):
                try:
                    text = page.extract_text().splitlines()
                    i = 0
                    end = i + n_lines
                    while end < len(text):
                        txt = " ".join(text[i:end])
                        txt = process_line(txt, n_lines=n_lines)
                        if txt is not None:
                            pdf_text.append(txt)

                        i += n_lines
                        end = i + n_lines
                    if end >= len(text):
                        txt = " ".join(text[i:])
                        txt = process_line(txt, n_lines=n_lines)
                        if txt is not None:
                            pdf_text.append(txt)
                except Exception as e:
                    msg.fail(
                        f"Could not extract text from page {pn} of file: {file}",
                        f"\t{e}",
                        spaced=True,
                    )
        except Exception as e:
            msg.fail(f"Could not extract text from file: {file}", f"\t{e}", spaced=True)
            return []
        return flatten_list(pdf_text)
    else:
        return []


def extract_text_list(data_path, n_lines=2):
    try:
        pdfs = resolve_data_path(data_path)
    except Exception as e:
        msg.fail(f"Could not resolve data path: {data_path}", f"\t{e}", spaced=True)
        return []
    text_list = []
    for file in pdfs:
        if Path(file).suffix == ".pdf":
            try:
                pdf_text = extract_text(file, n_lines=n_lines)
                text_list.append(flatten_list(pdf_text))
            except Exception as e:
                msg.fail(
                    f"Could not extract text from file: {file}", f"\t{e}", spaced=True
                )
    return text_list


def extract_text_dict(data_path, n_lines=2):
    try:
        pdfs = resolve_data_path(data_path)
    except Exception as e:
        msg.fail(f"Could not resolve data path: {data_path}", f"\t{e}", spaced=True)
        return []
    pdf_dict = {}
    for file in pdfs:
        if Path(file).suffix == ".pdf":
            try:
                pdf_text = extract_text(file, n_lines=n_lines)
                pdf_dict[str(file)] = flatten_list(pdf_text)
            except Exception as e:
                msg.fail(
                    f"Could not extract text from file: {file}", f"\t{e}", spaced=True
                )
    return pdf_dict


# def extract_text_list(data_path, n_lines=2):
#     pdfs = resolve_data_path(data_path)
#     text_list = []
#     for file in pdfs:
#         if Path(file).suffix == ".pdf":
#             try:
#                 pdf = PdfReader(str(file))
#                 pdf_text = []
#                 for page in pdf.pages:
#                     text = page.extract_text().splitlines()
#                     i = 0
#                     end = i + n_lines
#                     while end < len(text):
#                         txt = " ".join(text[i:end])
#                         txt = process_line(txt, n_lines=n_lines)
#                         if txt is not None:
#                             pdf_text.append(txt)

#                         i += n_lines
#                         end = i + n_lines
#                     if end >= len(text):
#                         txt = " ".join(text[i:])
#                         txt = process_line(txt, n_lines=n_lines)
#                         if txt is not None:
#                             pdf_text.append(txt)
#                 text_list.append(flatten_list(pdf_text))
#             except Exception as e:
#                 msg.fail(f"Could not extract text from file: {file}\n{e}")
#     return text_list

