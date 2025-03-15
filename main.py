import PyPDF2
#taking in a pdf, converting it to text
#(all happening locally for now)
#text is used to make reels

text = "".join(page.extract_text() for page in PyPDF2.PdfReader(open("Lecture11-Trees.pdf", "rb")).pages)
