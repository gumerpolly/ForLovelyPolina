import PyPDF2
import os

def pdf_to_txt(pdf_path, output_path=None):
    """
    Преобразует PDF файл в текстовый формат
    
    Args:
        pdf_path: путь к PDF файлу
        output_path: путь для сохранения текста, по умолчанию - то же имя, но с расширением .txt
    
    Returns:
        путь к сохраненному текстовому файлу
    """
    if output_path is None:
        base_name = os.path.splitext(pdf_path)[0]
        output_path = f"{base_name}.txt"
    
    text = ""
    with open(pdf_path, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text() + "\n\n"
    
    with open(output_path, 'w', encoding='utf-8') as txt_file:
        txt_file.write(text)
    
    return output_path

if __name__ == "__main__":
    pdf_path = "Исходный текст 1.pdf"
    output_path = pdf_to_txt(pdf_path)
    print(f"Текст сохранен в файл: {output_path}")
