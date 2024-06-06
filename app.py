import app

from time import ticks_ms
from app_components import clear_background
from events.input import Buttons, BUTTON_TYPES


class KeyboardApp(app.App):

    shift = "\u2191"
    space = "    "
    backspace = "\u2190"
    confirm = "OK"
    alphabet = [
                "abcdefghijklmnopqrstuvwxyz",
                "ABCDEFGHIJKLMNOPQRSTUVWXYZ",
                "1234567890.-+*/=^()<>[]{}",
                "\"£$%&_;'#,:@~!?"
               ]
    # Shift, space, backspace, confirm
    _control_keys = [shift, space, backspace, confirm]
    _key_width = 22
    _key_height = 22
    _key_font_size = 10
    _columns = 9
    
    KEYBOARD_STATE = 0
    CONTROL_STATE = 1
    CURSOR_STATE = 2

    def __init__(self):
        self.button_states = Buttons(self)
        self.message = "Enter SSID"
        self.text = ""
        self.masked = False
        self.current = [0, 0]
        self.control = 0
        self.cursor = 0
        self.state = self.KEYBOARD_STATE
        self.buttons_down = {
            BUTTON_TYPES["CANCEL"]: self.button_states.get(BUTTON_TYPES["CANCEL"]),
            BUTTON_TYPES["CONFIRM"]: self.button_states.get(BUTTON_TYPES["CONFIRM"]),
            BUTTON_TYPES["UP"]: self.button_states.get(BUTTON_TYPES["UP"]),
            BUTTON_TYPES["DOWN"]: self.button_states.get(BUTTON_TYPES["DOWN"]),
            BUTTON_TYPES["LEFT"]: self.button_states.get(BUTTON_TYPES["LEFT"]),
            BUTTON_TYPES["RIGHT"]: self.button_states.get(BUTTON_TYPES["RIGHT"]),
        }
    
    def reset(self):
        self.text = ""
        self.current = [0, 0]
        self.control = 0
        self.state = self.KEYBOARD_STATE

    def update(self, delta):
        if self.button_states.get(BUTTON_TYPES["CANCEL"]) and not self.buttons_down[BUTTON_TYPES["CANCEL"]]:
            self.button_states.clear()
            self.minimise()
            self.reset()

        if self.button_states.get(BUTTON_TYPES["CONFIRM"]) and not self.buttons_down[BUTTON_TYPES["CONFIRM"]]:
            if self.state == self.CURSOR_STATE:
                return
            elif self.state == self.KEYBOARD_STATE:
                self.text = self.text[:self.cursor] + self.alphabet[self.current[0]][self.current[1]] + self.text[self.cursor:]
                self.cursor += 1
            else:
                if self._control_keys[self.control] == self.shift:
                    self.current[0] = (self.current[0] + 1) % len(self.alphabet)
                elif self._control_keys[self.control] == self.space:
                    self.text = self.text[:self.cursor] + " " + self.text[self.cursor:]
                    self.cursor += 1
                elif self._control_keys[self.control] == self.backspace:
                    self.text = self.text[:self.cursor - 1] + self.text[self.cursor:]
                    self.cursor -= 1
                elif self._control_keys[self.control] == self.confirm:
                    self._result = self.text
                    self.button_states.clear()
                    self.minimise()
                    self.reset()

        if self.button_states.get(BUTTON_TYPES["UP"]) and not self.buttons_down[BUTTON_TYPES["UP"]]:
            if self.state == self.CURSOR_STATE:
                return
            elif self.state == self.CONTROL_STATE:
                self.state = self.KEYBOARD_STATE
                if self.current[1] >= len(self.alphabet[self.current[0]]):
                    self.current[1] = min(self.current[1], len(self.alphabet[self.current[0]]) - 1)
            else:
                if self.current[1] < self._columns:
                    self.state = self.CURSOR_STATE
                else:
                    self.current[1] -= self._columns

        if self.button_states.get(BUTTON_TYPES["DOWN"]) and not self.buttons_down[BUTTON_TYPES["DOWN"]]:
            if self.state == self.CONTROL_STATE:
                return
            elif self.state == self.CURSOR_STATE:
                self.state = self.KEYBOARD_STATE
            else:
                if int(self.current[1] / self._columns) == int(len(self.alphabet[self.current[0]]) / self._columns):
                    self.state = self.CONTROL_STATE
                else:
                    self.current[1] = min(self.current[1] + self._columns, len(self.alphabet[self.current[0]]) - 1)

        if self.button_states.get(BUTTON_TYPES["RIGHT"]) and not self.buttons_down[BUTTON_TYPES["RIGHT"]]:
            if self.state == self.KEYBOARD_STATE:
                row = int(self.current[1] / self._columns)
                new_index_full_row = ((self.current[1] + 1) % self._columns) + row * self._columns
                if new_index_full_row < len(self.alphabet[self.current[0]]):
                    self.current[1] = new_index_full_row
                else:
                    self.current[1] = row * self._columns
            elif self.state == self.CONTROL_STATE:
                self.control = (self.control + 1) % len(self._control_keys)
            elif self.state == self.CURSOR_STATE and self.text != "":
                self.cursor = (self.cursor + 1) % (len(self.text) + 1)

        if self.button_states.get(BUTTON_TYPES["LEFT"]) and not self.buttons_down[BUTTON_TYPES["LEFT"]]:
            if self.state == self.KEYBOARD_STATE:
                row = int(self.current[1] / self._columns)
                new_index_full_row = ((self.current[1] + self._columns - 1) % self._columns) + row * self._columns
                self.current[1] = min(new_index_full_row, len(self.alphabet[self.current[0]]) - 1)
            elif self.state == self.CONTROL_STATE:
                self.control = (self.control + len(self._control_keys) - 1) % len(self._control_keys)
            elif self.state == self.CURSOR_STATE and self.text != "":
                self.cursor = (self.cursor + len(self.text)) % (len(self.text) + 1)
                
        self.buttons_down[BUTTON_TYPES["CANCEL"]] = self.button_states.get(BUTTON_TYPES["CANCEL"])
        self.buttons_down[BUTTON_TYPES["CONFIRM"]] = self.button_states.get(BUTTON_TYPES["CONFIRM"])
        self.buttons_down[BUTTON_TYPES["UP"]] = self.button_states.get(BUTTON_TYPES["UP"])
        self.buttons_down[BUTTON_TYPES["DOWN"]] = self.button_states.get(BUTTON_TYPES["DOWN"])
        self.buttons_down[BUTTON_TYPES["LEFT"]] = self.button_states.get(BUTTON_TYPES["LEFT"])
        self.buttons_down[BUTTON_TYPES["RIGHT"]] = self.button_states.get(BUTTON_TYPES["RIGHT"])

    def draw_message(self, ctx):
        ctx.font_size = 26
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE

        ctx.rgb(1, 1, 1)
        
        # Prompt
        ctx.move_to(0, -60).text(self.message)
        # Current text
        txt = self.text if not self.masked else ("*" * len(self.text))
        ctx.move_to(0, -35).text(txt)
        # Cursor
        if self.state == self.CURSOR_STATE:
            ctx.rgba(255, 255, 255, 1.0)
        else:
            ctx.rgba(255, 255, 255, 0.5)
        if ticks_ms() % 1000 < 500:
            ctx.move_to(ctx.text_width(self.text[:self.cursor]) - ctx.text_width(self.text) / 2, -35)
            ctx.text("|")

    def _draw_key(self, ctx, x, y, w, h, txt, selected):
        ctx.move_to(x, y)
        # Background
        if selected:
            ctx.rgb(0.2, 0.2, 0.2)
        else:
            ctx.rgb(0, 0, 0)
        ctx.rectangle(x, y, w, h).fill()
        # Border
        if selected:
            ctx.rgba(255, 255, 255, 1.0)
        else:
            ctx.rgba(255, 255, 255, 0.5)
        ctx.rectangle(x, y, w, h).stroke()
        # Character
        ctx.move_to(x + w / 2, y + h / 2)
        ctx.text(txt)

    def draw(self, ctx):
        clear_background(ctx)
        ctx.save()

        # Draw prompt
        self.draw_message(ctx)
        
        ctx.font_size = 26
        ctx.text_align = ctx.CENTER
        ctx.text_baseline = ctx.MIDDLE
        
        # Draw character keys
        start = 0
        end = min(self._columns, len(self.alphabet[self.current[0]]))
        while end != start:
            range = end - start
            for col in range(range):
                x = self._key_width * (col - range / 2)
                y = -10 + int(start / self._columns) * self._key_height
                txt = self.alphabet[self.current[0]][col + start]
                selected = self.state == self.KEYBOARD_STATE and (self.current[1] == col + start)
                self._draw_key(ctx, x, y, self._key_width * len(txt), self._key_height, txt, selected)
                
            start = end
            end = min(start + self._columns, len(self.alphabet[self.current[0]]))
        
        # Draw control keys
        row_character_length = sum([len(item) for item in self._control_keys])
        y = -10 + (1 + int(len(self.alphabet[self.current[0]]) / self._columns)) * self._key_height
        previous_characters = 0
        for i in range(len(self._control_keys)):
            item = self._control_keys[i]
            x = self._key_width * (previous_characters - row_character_length / 2)
            selected = self.state == self.CONTROL_STATE and (self.control == i)
            self._draw_key(ctx, x, y, self._key_width * len(item), self._key_height, item, selected)
            previous_characters += len(item)
        
        ctx.restore()

__app_export__ = KeyboardApp
