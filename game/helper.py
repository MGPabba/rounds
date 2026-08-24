# ------------------------------
# FLOATING TEXT CLASS
# ------------------------------

class FloatingText:
    def __init__(self, color, x, y, text):
        # floating text info
        self.color = color
        self.x = x
        self.y = y
        self.text = text
        self.timer = 120
        self.active = True
    
    def update(self):
        # move text up and decrease timer, disappear when timer runs out
        self.y -= 1
        self.timer -= 1
        if self.timer <= 0:
            self.active = False

# ------------------------------
# HELPER FUNCTIONS
# ------------------------------

def wrap_text(text, regular_font, max_width):
    # split the text into a list of words
    words = text.split(' ')
    lines = []
    current_line = ""

    for word in words:
        # check if adding the next word to the current line exceeds the max width
        test_line = f"{current_line} {word}".strip()
        if regular_font.size(test_line)[0] <= max_width:
            current_line = test_line
        else:
            # add the current line to list of lines if its over the max width
            lines.append(current_line.strip())
            current_line = word

    # add the last line
    if current_line:
        lines.append(current_line.strip())

    return lines

def dynamic_text(font_cache, text, max_width, max_height, color):
    # default font size
    font_size = 30

    # decrease font size until it fits within the max width and height
    while font_size > 10:
        temp_font = font_cache[font_size]
        text_width, text_height = temp_font.size(text)
        if text_width <= max_width and text_height <= max_height:
            return temp_font.render(text, True, color)
        font_size -= 1

    # use the smallest font if text is too long
    smallest_font = font_cache[10]
    return smallest_font.render(text, True, color)
