import json
from pynput import keyboard, mouse
from time import sleep

class Contloller:
    """Control mouse and keyboard"""
    wait = 0.5

    def __init__(self):
        self.mouse = mouse.Controller()
        self.keyboard = keyboard.Controller()

    def waiter(argument):
        """Wait set seconds

        Args:
            argument (float): seconds to wait
        """
        def decorator(function):
            def wrapper(*args, **kwargs):
                sleep(argument)
                result = function(*args, **kwargs)
                return result
            return wrapper
        return decorator

    @waiter(wait)
    def click_button(self, button):
        """Click keyboard button

        Args:
            button (mouse.Button): button to clikc
        """
        self.keyboard.press(button)
        self.keyboard.release(button)

    @waiter(wait)
    def type(self, text):
        """Type on keyboard

        Args:
            text (str): text to type
        """
        self.keyboard.type(text)

    @waiter(wait)
    def press_and_hold(self, hold_button, pressed_button):
        """Press and hold seleced button

        Args:
            hold_button (mouse.Button): button to hold
            pressed_button (mouse.Button): button to press
        """
        with self.keyboard.pressed(hold_button):
            self.keyboard.press(pressed_button)

    @waiter(wait)
    def click_at_position(self, x_cord, y_cord, button=mouse.Button.left):
        """Click using mouse in selected position

        Args:
            x_cord (int): x position of mouse
            y_cord (int): y position of mouse
            button (mouse.Button, optional): button on mouse to click. Defaults to mouse.Button.left.
        """
        self.mouse.position = (x_cord, y_cord)
        self.mouse.click(button, 1)

    @waiter(wait)
    def set_position(self, x_cord, y_cord):
        """Set cursor on given position

        Args:
            x_cord (int): x position of mouse
            y_cord (int): y position of mouse
        """
        self.mouse.position = (x_cord, y_cord)

    @waiter(wait)
    def press_mouse_button(self, button=mouse.Button.left):
        """Press mouse button

        Args:
            button (mouse.Button, optional): button to press. Defaults to mouse.Button.left.
        """
        self.mouse.press(button)

    def release_mouse_button(self, button=mouse.Button.left):
        """Release mouse button

        Args:
            button (mouse.Button, optional): button to release. Defaults to mouse.Button.left.
        """
        self.mouse.release(button)

    def move_pointer(self, dx=0, dy=0):
        """Move cursor to specified position

        Args:
            dx (int, optional): x position of mouse to move. Defaults to 0.
            dy (int, optional): y position of mouse to move. Defaults to 0.
        """
        self.mouse.move(
            dx=dx,
            dy=dy
        )

class Process:
    """Add additional functionality to the conrtroller option
    """
    def __init__(self, filename, controller):
        self.filename = filename
        self.steps = []
        self.controller = controller

    def load_steps(self):
        """Reads the contents of the specified json file
        """
        with open(self.filename) as file:
            self.steps = json.load(file)['steps']

    def draw_line(self, start_x, start_y, lenght):
        """Draws lines

        Args:
            start_x (int): x position on the monitor axis
            start_y (int): y position on the monitor axis
            lenght (int): line length
        """
        self.controller.set_position(start_x, start_y)
        self.controller.press_mouse_button()

        for _ in range(int(lenght/10)):
            self.controller.move_pointer(dx=2)

        self.controller.release_mouse_button()

    def start(self):
        """Performs the indicated actions downloaded from the json file
        """
        options = {
            "Type": self.controller.type,
            "Click button": lambda button: self.controller.click_button(getattr(keyboard.Key, button)), #@TODO: enumeny dopatrzeć
            "Hold and press": lambda hold_button, pressed_button: self.controller.press_and_hold(
                                getattr(keyboard.Key, hold_button), getattr(keyboard.Key, pressed_button)),
            "Click at position": self.controller.click_at_position,
            "Set position": self.controller.click_at_position,
            "Press mouse button": self.controller.press_mouse_button,
            "Release mouse button": self.controller.release_mouse_button,
            "Draw line": self.draw_line
        }

        for step in self.steps:
            for key, value in step.items():
                options[key](**value)

def main():
    controller = Contloller()
    process = Process('actions.json', controller)
    process.load_steps()
    process.start()

    # controller.click_button(keyboard.Key.cmd_l)
    # controller.type('Paint')
    # controller.click_button(keyboard.Key.enter)
    # controller.press_and_hold(keyboard.Key.cmd_l, keyboard.Key.up)
    # controller.click_at_position(283, 72)
    # controller.click_at_position(705, 107)
    # controller.click_at_position(736, 265)
    # controller.click_at_position(964, 62)
    # controller.set_position(112, 498)

if __name__ == '__main__':
    main()
