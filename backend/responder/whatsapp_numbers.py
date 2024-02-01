import re
def get_list_of_whatsapp_numbers(text):
    pattern = r"(?i)whatsapp[\s\S]+?(?=\,|\.|\n|$)" # Regular expression pattern for 'WhatsApp' followed by any characters and a phone number
    whatsapp_segments = re.findall(pattern, text) # Find all 'WhatsApp' segments in the text
    number_pattern = r"(\+?\d{2,4}[\s-]?\d{3,4}[\s-]?\d{3,6}|00\d{2,3}[\s-]?\d{3,4}[\s-]?\d{3,6})"
    numbers = []
    for segment in whatsapp_segments:
        numbers.extend(re.findall(number_pattern, segment))
    formatted_numbers = list({re.sub(r"^00", "+", re.sub(r"[\s-]", "", num)) for num in numbers}) # Remove duplicates
    return formatted_numbers if formatted_numbers else None 