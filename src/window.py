# window.py
#
# Copyright 2024 Schlemuel
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# SPDX-License-Identifier: GPL-3.0-or-later

from gi.repository import Adw, Gtk, Gio, Gdk, GLib, PangoCairo, Pango
import io, cairo
from gettext import gettext as _

@Gtk.Template(resource_path='/io/github/SamuelSchlemperSchlemuel/SingWriter/window.ui')
class SingwriterWindow(Adw.ApplicationWindow):
    __gtype_name__ = 'SingwriterWindow'

    grid = Gtk.Template.Child()
    symbol_screen_button = Gtk.Template.Child()
    symbol_screen = Gtk.Template.Child()
    remove_character_button = Gtk.Template.Child()
    break_line_button = Gtk.Template.Child()
    space_button = Gtk.Template.Child()

    boxes = dict()
    current_box = None
    text_list = list()

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.grid_row_quantity = 8
        self.grid_column_quantity = 6
        self.add_grid_size(grid = self.grid,
                           row_quantity = self.grid_row_quantity,
                           column_quantity = self.grid_column_quantity,
                           boxes = True)

        style_provider = Gtk.CssProvider()
        resource_path_style = '/io/github/SamuelSchlemperSchlemuel/SingWriter/style.css'
        style_provider.load_from_path(f'resource://{resource_path_style}')

        symbol_screen = SymbolScreen(self)
        self.symbol_screen_grid = symbol_screen.symbol_screen_grid

        scrolled_window = Gtk.ScrolledWindow()
        scrolled_window.set_child(self.symbol_screen_grid)
        scrolled_window.set_vexpand(True)
        scrolled_window.set_hexpand(True)

        self.revealer = Gtk.Revealer()
        self.revealer.set_child(scrolled_window)
        self.revealer.set_reveal_child(False)
        self.revealer.set_vexpand(True)
        self.revealer.set_hexpand(True)

        self.symbol_screen.append(self.revealer)

        self.page_width = 595
        self.page_height = 842
        self.font_size = 20

        save_file = SaveFile(self)

        kwargs['application'].create_action('change-grid-size', self.change_grid_size)
        kwargs['application'].create_action('change-font-size', self.change_font_size)
        kwargs['application'].create_action('change-pdf-size', self.change_pdf_size)
        kwargs['application'].create_action('save-pdf', save_file.dialog)

        self.symbol_screen_button.connect('clicked', self.push_screen)
        self.remove_character_button.connect('clicked', self.back_space)
        self.break_line_button.connect('clicked', self.break_line)
        self.space_button.connect('clicked', self.space)

        self.add_controller(self.create_shortcut_controller())

    def add_grid_size(self, grid, row_quantity, column_quantity, boxes):
        for num in range(row_quantity):
            grid.insert_row(num)

        for num in range(column_quantity):
            grid.insert_column(num)

        if boxes:
            self.text_list = list()

        for row in range(row_quantity):
            for column in range(column_quantity):
                box = Gtk.Box()

                gesture = Gtk.GestureClick()
                gesture.connect("pressed", self.select_box)
                gesture.id = f'{column}_{row}'
                box.add_controller(gesture)

                if boxes:
                    label = Gtk.Label()
                    label.get_style_context().add_class('character_label')
                    box.append(label)
                    self.text_list.append('')

                    box.get_style_context().add_class('box')
                    self.boxes[f'{column}_{row}'] = box

                grid.attach(box, column, row, 1, 1)

    def change_grid_size(self, *args):
        dialog = GridSizeDialog(self)
        dialog.show()

    def change_font_size(self, *args):
        dialog = FontSizeDialog(self)
        dialog.show()

    def change_pdf_size(self, *args):
        dialog = PdfSizeDialog(self)
        dialog.show()

    def push_screen(self, widget):
        # Push the button screen with the symbols

        current_reveal_state = self.revealer.get_reveal_child()

        if not current_reveal_state:
            self.revealer.get_style_context().remove_class('noRevealer')
            self.revealer.get_style_context().add_class('revealer')
            self.symbol_screen_button.set_icon_name('pan-down-symbolic')
        else:
            self.revealer.get_style_context().remove_class('revealer')
            self.revealer.get_style_context().add_class('noRevealer')
            self.symbol_screen_button.set_icon_name('pan-up-symbolic')

        self.revealer.set_reveal_child(not current_reveal_state)

    def select_box(self, gesture, *args):
        #Activated when the user clicks in a box

        marked = dict()

        if self.current_box == None:
            self.boxes[gesture.id].get_style_context().add_class('yellow')
            self.current_box = gesture.id
        elif self.current_box == gesture.id:
            self.boxes[self.current_box].get_style_context().remove_class('yellow')
            self.current_box = None
        else:
            self.boxes[self.current_box].get_style_context().remove_class('yellow')
            self.boxes[gesture.id].get_style_context().add_class('yellow')
            self.current_box = gesture.id

    def back_space(self, *args):
        if self.current_box != None:
            box = self.boxes[self.current_box]
            label = box.get_last_child()
            current_text = label.get_label()
            new_text = current_text[:-1]
            label.set_text(new_text)

            position = int(self.current_box[2]) * self.grid_column_quantity + int(self.current_box[0])
            self.text_list[position] = self.text_list[position][:-1]

    def break_line(self, *args):
        if self.current_box != None:
            box = self.boxes[self.current_box]
            label = box.get_last_child()
            current_text = label.get_label()
            new_text = current_text + '\n'
            label.set_text(new_text)

            position = int(self.current_box[2]) * self.grid_column_quantity + int(self.current_box[0])
            self.text_list[position] += '\n'

    def space(self, *args):
        if self.current_box != None:
            box = self.boxes[self.current_box]
            label = box.get_last_child()
            current_text = label.get_label()
            new_text = current_text + ' '
            label.set_text(new_text)

            position = int(self.current_box[2]) * self.grid_column_quantity + int(self.current_box[0])
            self.text_list[position] += ' '

    def right(self, *args):
        if self.current_box != None:
            gesture = Gtk.GestureClick()

            if self.current_box[0] == f'{self.grid_column_quantity - 1}':
                if self.current_box[2] == f'{self.grid_row_quantity - 1}':
                    gesture.id = '0_0'
                else:
                    gesture.id = f'0_{int(self.current_box[2]) + 1}'
            else:
                gesture.id = f'{int(self.current_box[0]) + 1}_{self.current_box[2]}'

            self.select_box(gesture)

    def left(self, *args):
        if self.current_box != None:
            gesture = Gtk.GestureClick()

            if self.current_box[0] == '0':
                if self.current_box[2] == f'0':
                    gesture.id = f'{self.grid_column_quantity - 1}_{self.grid_row_quantity - 1}'
                else:
                    gesture.id = f'{self.grid_column_quantity - 1}_{int(self.current_box[2]) - 1}'
            else:
                gesture.id = f'{int(self.current_box[0]) - 1}_{self.current_box[2]}'

            self.select_box(gesture)

    def up(self, *args):
        if self.current_box != None:
            gesture = Gtk.GestureClick()

            if self.current_box[2] == f'0':
                gesture.id = f'{self.current_box[0]}_{self.grid_row_quantity - 1}'
            else:
                gesture.id = f'{self.current_box[0]}_{int(self.current_box[2]) - 1}'

            self.select_box(gesture)

    def down(self, *args):
         if self.current_box != None:
            gesture = Gtk.GestureClick()

            if self.current_box[2] == f'{self.grid_row_quantity - 1}':
                gesture.id = f'{self.current_box[0]}_0'
            else:
                gesture.id = f'{self.current_box[0]}_{int(self.current_box[2]) + 1}'

            self.select_box(gesture)

    def create_shortcut_controller(self):
        shortcut_controller = Gtk.ShortcutController.new()

        shortcut_break_line = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("<Ctrl>Return"),
            action=Gtk.CallbackAction.new(callback=self.break_line)
        )

        shortcut_space = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("<Ctrl>space"),
            action=Gtk.CallbackAction.new(callback=self.space)
        )

        shortcut_back_space = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("<Ctrl>BackSpace"),
            action=Gtk.CallbackAction.new(callback=self.back_space)
        )

        shortcut_right = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("Right"),
            action=Gtk.CallbackAction.new(callback=self.right)
        )

        shortcut_left = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("Left"),
            action=Gtk.CallbackAction.new(callback=self.left)
        )

        shortcut_up = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("Up"),
            action=Gtk.CallbackAction.new(callback=self.up)
        )

        shortcut_down = Gtk.Shortcut.new(
            trigger=Gtk.ShortcutTrigger.parse_string("Down"),
            action=Gtk.CallbackAction.new(callback=self.down)
        )

        shortcut_controller.add_shortcut(shortcut_break_line)
        shortcut_controller.add_shortcut(shortcut_space)
        shortcut_controller.add_shortcut(shortcut_back_space)
        shortcut_controller.add_shortcut(shortcut_right)
        shortcut_controller.add_shortcut(shortcut_left)
        shortcut_controller.add_shortcut(shortcut_up)
        shortcut_controller.add_shortcut(shortcut_down)

        return shortcut_controller

class GridSizeDialog(Gtk.Dialog):

    def __init__(self, parent):
        super().__init__(title=_("Change grid size"), transient_for=parent, modal=True)
        self.parent = parent

        adjustment_row = Gtk.Adjustment(value=1, lower=1, upper=999, step_increment=1, page_increment=10, page_size=0)
        self.spin_button_row = Gtk.SpinButton()
        self.spin_button_row.set_adjustment(adjustment_row)
        self.spin_button_row.set_numeric(True)

        adjustment_column = Gtk.Adjustment(value=1, lower=1, upper=10, step_increment=1, page_increment=10, page_size=0)
        self.spin_button_column = Gtk.SpinButton()
        self.spin_button_column.set_adjustment(adjustment_column)
        self.spin_button_column.set_numeric(True)

        button = Gtk.Button(label=_('Change grid size'))
        button.connect('clicked', self.actualize_grid_size)

        label_row = Gtk.Label(label=_('Number of rows'))
        label_column = Gtk.Label(label=_('Number of columns'))

        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        box.append(label_row)
        box.append(self.spin_button_row)
        box.append(label_column)
        box.append(self.spin_button_column)
        box.append(button)

        content_area = self.get_content_area()
        content_area.append(box)

    def actualize_grid_size(self, widget):
        self.remove_grid_children()
        self.parent.grid_row_quantity = self.spin_button_row.get_value_as_int()
        self.parent.grid_column_quantity = self.spin_button_column.get_value_as_int()
        self.parent.add_grid_size(grid = self.parent.grid,
                                  row_quantity = self.parent.grid_row_quantity,
                                  column_quantity = self.parent.grid_column_quantity,
                                  boxes = True)
        self.response(Gtk.ResponseType.OK)
        self.close()

    def remove_grid_children(self):
        # Clean the grid with the boxes

        self.parent.current_box = None

        if self.parent.grid_row_quantity < self.parent.grid_column_quantity:
            for num in range(self.parent.grid_row_quantity):
                self.parent.grid.remove_row(0)
        else:
            for num in range(self.parent.grid_column_quantity):
                self.parent.grid.remove_column(0)

class FontSizeDialog(Gtk.Dialog):

    def __init__(self, parent):
        super().__init__(title=_("Change font size"), transient_for=parent, modal=True)
        self.parent = parent

        adjustment = Gtk.Adjustment(value=20, lower=10, upper=50, step_increment=1, page_increment=10, page_size=0)
        self.spin_button = Gtk.SpinButton()
        self.spin_button.set_adjustment(adjustment)
        self.spin_button.set_numeric(True)

        button = Gtk.Button(label=_('Change font size'))
        button.connect('clicked', self.actualize_font_size)

        label = Gtk.Label(label=_('The font size in the final pdf (does not change the font of the grid)'))

        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        box.append(label)
        box.append(self.spin_button)
        box.append(button)

        content_area = self.get_content_area()
        content_area.append(box)

    def actualize_font_size(self, widget):
        self.parent.font_size = self.spin_button.get_value_as_int()
        self.response(Gtk.ResponseType.OK)
        self.close()

class PdfSizeDialog(Gtk.Dialog):

    def __init__(self, parent):
        super().__init__(title=_("Change pdf size"), transient_for=parent, modal=True)
        self.parent = parent

        adjustment_height = Gtk.Adjustment(value=self.parent.page_height, lower=100, upper=5000, step_increment=20, page_increment=10, page_size=0)
        self.spin_button_height = Gtk.SpinButton()
        self.spin_button_height.set_adjustment(adjustment_height)
        self.spin_button_height.set_numeric(True)

        adjustment_width = Gtk.Adjustment(value=self.parent.page_width, lower=100, upper=5000, step_increment=20, page_increment=10, page_size=0)
        self.spin_button_width = Gtk.SpinButton()
        self.spin_button_width.set_adjustment(adjustment_width)
        self.spin_button_width.set_numeric(True)

        button = Gtk.Button(label=_('Change pdf size'))
        button.connect('clicked', self.actualize_pdf_size)

        label_height = Gtk.Label(label=_('Height pdf'))
        label_width = Gtk.Label(label=_('Width pdf'))

        box = Gtk.Box(spacing=6, orientation=Gtk.Orientation.VERTICAL)
        box.append(label_height)
        box.append(self.spin_button_height)
        box.append(label_width)
        box.append(self.spin_button_width)
        box.append(button)

        content_area = self.get_content_area()
        content_area.append(box)

    def actualize_pdf_size(self, widget):
        self.parent.page_height = self.spin_button_height.get_value_as_int()
        self.parent.page_width = self.spin_button_width.get_value_as_int()
        self.response(Gtk.ResponseType.OK)
        self.close()

class SymbolScreen():
    def __init__(self, parent):
        self.parent = parent
        self.symbol_screen_content()

    def symbol_screen_content(self):
        self.hand_format = Gtk.Button(label=_("Hand format"))
        self.movement = Gtk.Button(label=_("Movement"))
        self.sing_local = Gtk.Button(label=_("Signal Location"))
        self.transformation = Gtk.Button(label=_("Transformation"))

        self.hand_format.connect('clicked', self.hand_format_screen)
        self.movement.connect('clicked', self.movement_screen)
        self.sing_local.connect('clicked', self.sing_local_screen)
        self.transformation.connect('clicked', self.transformation_screen)

        self.hand_format.get_style_context().add_class('button_content_reveal')
        self.movement.get_style_context().add_class('button_content_reveal')
        self.sing_local.get_style_context().add_class('button_content_reveal')
        self.transformation.get_style_context().add_class('button_content_reveal')

        self.symbol_screen_grid = Gtk.Grid()
        self.symbol_screen_grid.set_column_homogeneous(True)
        self.symbol_screen_grid.set_row_homogeneous(True)
        self.symbol_screen_grid.set_column_spacing(5)
        self.symbol_screen_grid.set_row_spacing(10)

        self.symbol_screen_grid_row_quantity = 23
        self.symbol_screen_grid_column_quantity = 12

        self.parent.add_grid_size(grid = self.symbol_screen_grid,
                           row_quantity = self.symbol_screen_grid_row_quantity,
                           column_quantity = self.symbol_screen_grid_column_quantity,
                           boxes = False)

        self.hand_format.emit('clicked')

    def hand_format_screen(self, widget):
        self.clean_symbol_screen_grid(23)

        characters_list = ['𝠀', '𝠁', '𝠂', '𝠃', '𝠄', '𝠅', '𝠆', '𝠇', '𝠈', '𝠉', '𝠊', '𝠋', '𝠌',
        '𝠍', '𝠎', '𝠏', '𝠐', '𝠑', '𝠒', '𝠓', '𝠔', '𝠕', '𝠖', '𝠘', '𝠗', '𝠙', '𝠚', '𝠛', '𝠜',
        '𝠝', '𝠞', '𝠟', '𝠠', '𝠡', '𝠢', '𝠣', '𝠤', '𝠥', '𝠦', '𝠧', '𝠨', '𝠩', '𝠪', '𝠫', '𝠬',
        '𝠭', '𝠮', '𝠯', '𝠰', '𝠱', '𝠲', '𝠳', '𝠴', '𝠵', '𝠶', '𝠷', '𝠸', '𝠹', '𝠺', '𝠻', '𝠼',
        '𝠽', '𝠾', '𝠿', '𝡀', '𝡁', '𝡂', '𝡃', '𝡄', '𝡅', '𝡆', '𝡇', '𝡈', '𝡉', '𝡊', '𝡋', '𝡌',
        '𝡍', '𝡏', '𝡎', '𝡐', '𝡑', '𝡒', '𝡓', '𝡔', '𝡕', '𝡖', '𝡗', '𝡘', '𝡙', '𝡚', '𝡛', '𝡜',
        '𝡝', '𝡞', '𝡟', '𝡠', '𝡡', '𝡢', '𝡣', '𝡤', '𝡥', '𝡦', '𝡧', '𝡨', '𝡩', '𝡪', '𝡫', '𝡬',
        '𝡭', '𝡮', '𝡯', '𝡰', '𝡱', '𝡲', '𝡳', '𝡴', '𝡵', '𝡶', '𝡷', '𝡸', '𝡹', '𝡺', '𝡻', '𝡼',
        '𝡽', '𝡾', '𝡿', '𝢀', '𝢁', '𝢂', '𝢃', '𝢄', '𝢅', '𝢆', '𝢇', '𝢈', '𝢉', '𝢊', '𝢋', '𝢌',
        '𝢍', '𝢎', '𝢏', '𝢐', '𝢑', '𝢒', '𝢓', '𝢔', '𝢕', '𝢖', '𝢗', '𝢘', '𝢙', '𝢚', '𝢛', '𝢜',
        '𝢝', '𝢞', '𝢟', '𝢠', '𝢡', '𝢢', '𝢣', '𝢤', '𝢥', '𝢦', '𝢧', '𝢨', '𝢩', '𝢪', '𝢫', '𝢬',
        '𝢭', '𝢮', '𝢰', '𝢱', '𝢯', '𝢲', '𝢳', '𝢴', '𝢵', '𝢶', '𝢷', '𝢸', '𝢹', '𝢺', '𝢻', '𝢼',
        '𝢽', '𝢾', '𝢿', '𝣀', '𝣁', '𝣂', '𝣃', '𝣄', '𝣅', '𝣆', '𝣇', '𝣈', '𝣉', '𝣊', '𝣋', '𝣌',
        '𝣍', '𝣎', '𝣏', '𝣐', '𝣑', '𝣒', '𝣓', '𝣔', '𝣕', '𝣖', '𝣗', '𝣘', '𝣙', '𝣚', '𝣛', '𝣜',
        '𝣝', '𝣞', '𝣟', '𝣠', '𝣡', '𝣢', '𝣣', '𝣤', '𝣥', '𝣦', '𝣧', '𝣨', '𝣩', '𝣪', '𝣫', '𝣬',
        '𝣭', '𝣮', '𝣯', '𝣰', '𝣱', '𝣲', '𝣳', '𝣴', '𝣵', '𝣶', '𝣷', '𝣸', '𝣹', '𝣺', '𝣻', '𝣼',
        '𝣽', '𝣾', '𝣿', '𝤀', '𝤁', '𝤂', '𝤃', '𝤄']

        self.add_characters(characters_list)

    def movement_screen(self, widget):
        self.clean_symbol_screen_grid(21)

        characters_list = ['𝤅', '𝤆', '𝤇', '𝤈', '𝤉', '𝤊', '𝤋', '𝤌', '𝤍', '𝤎', '𝤏',
        '𝤐', '𝤑', '𝤒', '𝤓', '𝤔', '𝤔', '𝤕', '𝤖', '𝤗', '𝤘', '𝤙', '𝤚', '𝤛', '𝤜', '𝤝',
        '𝤞', '𝤟', '𝤠', '𝤡', '𝤢', '𝤣', '𝤤', '𝤥', '𝤦', '𝤧', '𝤨', '𝤩', '𝤪', '𝤫', '𝤬',
        '𝤭', '𝤮', '𝤯', '𝤰', '𝤱', '𝤳', '𝤲', '𝤴', '𝤵', '𝤶', '𝤷', '𝤸', '𝤹', '𝤺', '𝤻',
        '𝤼', '𝤽', '𝤾', '𝤿', '𝥀', '𝥁', '𝥂', '𝥃', '𝥄', '𝥅', '𝥆', '𝥇', '𝥈', '𝥉', '𝥊',
        '𝥋', '𝥌', '𝥍', '𝥎', '𝥏', '𝥐', '𝥑', '𝥒', '𝥓', '𝥔', '𝥕', '𝥗', '𝥖', '𝥘', '𝥙',
        '𝥚', '𝥛', '𝥜', '𝥝', '𝥞', '𝥟', '𝥠', '𝥡', '𝥢', '𝥤', '𝥣', '𝥥', '𝥦', '𝥧', '𝥨',
        '𝥩', '𝥪', '𝥫', '𝥬', '𝥭', '𝥮', '𝥯', '𝥰', '𝥱', '𝥲', '𝥳', '𝥴', '𝥵', '𝥶', '𝥷',
        '𝥸', '𝥹', '𝥻', '𝥺', '𝥼', '𝥾', '𝥽', '𝥿', '𝦀', '𝦁', '𝦂', '𝦃', '𝦄', '𝦅', '𝦆',
        '𝦇', '𝦈', '𝦉', '𝦊', '𝦋', '𝦌', '𝦍', '𝦎', '𝦏', '𝦐', '𝦑', '𝦒', '𝦓', '𝦔', '𝦕',
        '𝦖', '𝦗', '𝦘', '𝦚', '𝦙', '𝦛', '𝦜', '𝦝', '𝦞', '𝦟', '𝦠', '𝦡', '𝦢', '𝦣', '𝦤',
        '𝦥', '𝦦', '𝦧', '𝦨', '𝦩', '𝦪', '𝦫', '𝦬', '𝦭', '𝦮', '𝦯', '𝧁', '𝧂', '𝧃', '𝧄',
        '𝧅', '𝧆', '𝧈', '𝧉', '𝧊', '𝧋', '𝧌', '𝧍', '𝧎', '𝧏', '𝧐', '𝧒', '𝧓', '𝧔', '𝧕',
        '𝧖', '𝧗', '𝧘', '𝧙', '𝧚', '𝧛', '𝧜', '𝧝', '𝧞', '𝧟', '𝧠', '𝧡', '𝧢', '𝧣', '𝧤',
        '𝧥', '𝧦', '𝧧', '𝧨', '𝧩', '𝧪', '𝧫', '𝧬', '𝧭', '𝧮', '𝧯', '𝧰', '𝧱', '𝧲', '𝧳',
        '𝧴', '𝧵', '𝧶', '𝧷', '𝧸', '𝧹', '𝧺', '𝧻', '𝧼', '𝧽', '𝧾']

        self.add_characters(characters_list)

    def sing_local_screen(self, widget):
        self.clean_symbol_screen_grid(8)

        characters_list = ['𝧿', '𝨷', '𝨸', '𝨹', '𝨺', '𝩭', '𝩮', '𝩯', '𝩰', '𝩱', '𝩲', '𝩳',
        '𝩴', '𝩶', '𝩷', '𝩸', '𝩹', '𝩺', '𝩻', '𝩼', '𝩽', '𝩾', '𝩿', '𝪀', '𝪁', '𝪂', '𝪃',
        '𝪅', '𝪆', '𝪇', '𝪈', '𝪉', '𝪊', '𝪋']

        self.add_characters(characters_list)

    def transformation_screen(self, widget):
        self.clean_symbol_screen_grid(14)

        characters_list = ['𝨀', '𝨁', '𝨂', '𝨃', '𝨄', '𝨅', '𝨆', '𝨇', '𝨈', '𝨉', '𝨊', '𝨋', '𝨌', '𝨍', '𝨏', '𝨎', '𝨑', '𝨒', '𝨓',
        '𝨔', '𝨕', '𝨖', '𝨗', '𝨘', '𝨙', '𝨚', '𝨜', '𝨛', '𝨞', '𝨝', '𝨟', '𝨠', '𝨡', '𝨢', '𝨣',
        '𝨥', '𝨤', '𝨦', '𝨧', '𝨨', '𝨩', '𝨪', '𝨫', '𝨬', '𝨭', '𝨮', '𝨯', '𝨰', '𝨱', '𝨲', '𝨳',
        '𝨴', '𝨵', '𝨶', '𝨼', '𝨻', '𝨽', '𝨾', '𝨿', '𝩀', '𝩂', '𝩁', '𝩃', '𝩄', '𝩅', '𝩆', '𝩇',
        '𝩈', '𝩉', '𝩊', '𝩋', '𝩌', '𝩍', '𝩎', '𝩏', '𝩐', '𝩑', '𝩒', '𝩓', '𝩔', '𝩖', '𝩕', '𝩗',
        '𝩘', '𝩙', '𝩚', '𝩛', '𝩜', '𝩝', '𝩞', '𝩟', '𝩠', '𝩡', '𝩢', '𝩣', '𝩤', '𝩥', '𝩦', '𝩧',
        '𝩨', '𝩩', '𝩪', '𝩫', '𝩬', '𝩵', '𝪄', ' ', ' ', '(𝢦)', '➝', '𝢈𝪛', '𝢦𝪜', '𝢦𝪝', '𝢦𝪞', '𝢦𝪟',
        '𝢦𝪡','𝢦𝪢', '𝢦𝪣', '𝢦𝪤', '𝢦𝪥', '𝢦𝪦', '𝢦𝪧', '𝢦𝪨', '𝢦𝪩', '𝢦𝪪', '𝢦𝪫', '𝢦𝪬', '𝢦𝪭', '𝢦𝪮', '𝢦𝪯']

        self.add_characters(characters_list)

    def clean_symbol_screen_grid(self, new_row_quantity):
        for row in range(self.symbol_screen_grid_row_quantity):
            for column in range(self.symbol_screen_grid_column_quantity):
                child = self.symbol_screen_grid.get_child_at(column, row)
                self.symbol_screen_grid.remove(child)

                if self.hand_format.get_parent():
                    self.hand_format.get_parent().remove(self.hand_format)

                if self.movement.get_parent():
                    self.movement.get_parent().remove(self.movement)

                if self.sing_local.get_parent():
                    self.sing_local.get_parent().remove(self.sing_local)

                if self.transformation.get_parent():
                    self.transformation.get_parent().remove(self.transformation)

        self.symbol_screen_grid_row_quantity = new_row_quantity

        self.parent.add_grid_size(grid = self.symbol_screen_grid,
                           row_quantity = self.symbol_screen_grid_row_quantity,
                           column_quantity = self.symbol_screen_grid_column_quantity,
                           boxes = False)

        self.symbol_screen_grid.attach(self.hand_format,       column = 0, row = 0, width = 3, height = 1)
        self.symbol_screen_grid.attach(self.movement,          column = 3, row = 0, width = 3, height = 1)
        self.symbol_screen_grid.attach(self.sing_local,        column = 6, row = 0, width = 3, height = 1)
        self.symbol_screen_grid.attach(self.transformation,    column = 9, row = 0, width = 3, height = 1)

    def add_characters(self, characters):
        row = 1
        col = 0

        for char in characters:
            label = Gtk.Label(label=char)
            label.get_style_context().add_class('character_label')

            box = Gtk.Box()
            box.append(label)

            gesture = Gtk.GestureClick()
            gesture.connect("pressed", self.select_character)
            gesture.id = f'{char}'
            box.add_controller(gesture)

            child = self.symbol_screen_grid.get_child_at(col, row)
            self.symbol_screen_grid.remove(child)
            self.symbol_screen_grid.attach(box, col, row, 1, 1)
            col += 1

            if col >= self.symbol_screen_grid_column_quantity:
                col = 0
                row += 1

    def select_character(self, gesture, clicks, horizontal, vertical):
        if self.parent.current_box != None:
            box = self.parent.boxes[self.parent.current_box]
            label = box.get_last_child()
            current_text = label.get_label()
            character = gesture.id

            change = ['(𝢦)', '➝', '𝢈𝪛', '𝢦𝪜', '𝢦𝪝', '𝢦𝪞', '𝢦𝪟', '𝢦𝪡','𝢦𝪢', '𝢦𝪣', '𝢦𝪤',
                      '𝢦𝪥', '𝢦𝪦', '𝢦𝪧', '𝢦𝪨', '𝢦𝪩', '𝢦𝪪', '𝢦𝪫', '𝢦𝪬', '𝢦𝪭', '𝢦𝪮', '𝢦𝪯']

            to = ['', '', '𝪛', '𝪜', '𝪝', '𝪞', '𝪟', '𝪡', '𝪢', '𝪣', '𝪤', '𝪥', '𝪦', '𝪧', '𝪨', '𝪩', '𝪪', '𝪫', '𝪬', '𝪭', '𝪮', '𝪯']

            if character in change:
                character = to[change.index(character)]

            label.set_text(current_text + character)

            position = int(self.parent.current_box[2]) * self.parent.grid_column_quantity + int(self.parent.current_box[0])
            self.parent.text_list[position] += character

class SaveFile():
    def __init__(self, parent):
        self.parent = parent

    def dialog(self, widget, _):
        file_dialog = Gtk.FileDialog()
        file_dialog.set_title("Save PDF")
        file_dialog.set_modal(True)
        file_dialog.save(self.parent, None, self.on_file_dialog_response)

    def on_file_dialog_response(self, dialog, result):
        file = dialog.save_finish(result)

        if file is not None:
          self.create_pdf(file)

    def create_pdf(self, file):
        x, y = 10, 50
        page_width = self.parent.page_width
        page_height = self.parent.page_height
        column_width = (page_width - 2*x) / self.parent.grid_column_quantity

        output_stream = io.BytesIO()
        surface = cairo.PDFSurface(output_stream, page_width, page_height)
        context = cairo.Context(surface)

        layout = PangoCairo.create_layout(context)
        font_desc = Pango.FontDescription(f"Noto Sans SignWriting {self.parent.font_size}")
        layout.set_font_description(font_desc)

        pdf_text = self.convert_list_to_text()

        lines = pdf_text.split('\n\n')

        for line in lines:
            columns = line.split('|')

            for i, column_text in enumerate(columns):
                layout.set_text(column_text, -1)
                column_x = x + i * column_width + (column_width - layout.get_pixel_size()[0]) / 2
                context.move_to(column_x, y)
                PangoCairo.show_layout(context, layout)

                if i < len(columns) - 1:
                    context.move_to(x + (i + 1) * column_width, y)
                    context.line_to(x + (i + 1) * column_width, page_height - y)
                    context.stroke()

            y += layout.get_pixel_size()[1] + 70

        surface.finish()
        pdf_data = GLib.Bytes.new(output_stream.getvalue())

        file.replace_contents_bytes_async(
            pdf_data,
            None,
            False,
            Gio.FileCreateFlags.NONE,
            None,
            self.save_file_complete
        )

    def save_file_complete(self, file, result):
        pass

    def convert_list_to_text(self):
        result_text = ''

        for i in range(len(self.parent.text_list)):
            if (i + 1) % self.parent.grid_column_quantity == 0:
                result_text += self.parent.text_list[i]
                result_text += '\n\n'
            else:
                result_text += self.parent.text_list[i] + '|'

        return result_text
