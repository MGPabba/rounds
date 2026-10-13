# helper.py

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------

def wrap_text(text, fonts, max_width):
    # split the text into a list of words
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:

        # check if adding the next word to the current line exceeds the max width
        test_line = f"{current_line} {word}".strip()
        if fonts[24].size(test_line)[0] <= max_width:
            current_line = test_line

        # add the current line to list of lines if its over the max width
        else:
            lines.append(current_line.strip())
            current_line = word

    # add the last line
    if current_line:
        lines.append(current_line.strip())

    return lines

def dynamic_text(font_cache, text_cache, text, max_width, max_height, color):
    # check if the text already exists
    cache_key = (text, max_width, max_height, color)
    if cache_key in text_cache:
        return text_cache[cache_key]

    # default font size
    font_size = 30

    # decrease font size until it fits within the max width and height
    while font_size > 10:
        temp_font = font_cache[font_size]
        text_width, text_height = temp_font.size(text)
        if text_width <= max_width and text_height <= max_height:
            rendered_text = temp_font.render(text, True, color)
            text_cache[cache_key] = rendered_text
            return rendered_text
        else:
            font_size -= 1

    # use the smallest font if text is too long
    smallest_font = font_cache[10]
    rendered_text = smallest_font.render(text, True, color)
    text_cache[cache_key] = rendered_text
    return rendered_text

def render_text(fonts, text_cache, font_size, text, color):
    # check if the text already exists
    cache_key = (font_size, text, color)
    if cache_key in text_cache:
        return text_cache[cache_key]

    # render the text and store it in the cache
    rendered_text = fonts[font_size].render(text, True, color)
    text_cache[cache_key] = rendered_text
    return rendered_text
