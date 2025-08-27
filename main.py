import kivy
from kivy.app import App
from kivy.lang import Builder
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.properties import NumericProperty, StringProperty, BooleanProperty, ObjectProperty, ListProperty
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.clock import Clock
from kivy.core.audio import SoundLoader
from plyer import filechooser
import math
import os
from functools import partial

# Kivy 앱의 최소 버전을 설정합니다.
kivy.require('2.1.0')

# JBNU Hold'em Main Tournament 기본 구조
# 형식: small/big/ante/duration(minutes)
DEFAULT_BLIND_STRUCTURE = (
    "100/200/200/15\n"
    "200/300/300/15\n"
    "200/400/400/15\n"
    "300/500/500/15\n"
    "300/600/600/15\n"
    "400/800/800/15\n"
    "500/1000/1000/15\n"
    "600/1200/1200/15\n"
    "800/1500/1500/15\n"
    "1000/1500/1500/15\n"
    "1000/2000/2000/12\n"
    "1500/2500/2500/12\n"
    "1500/3000/3000/12\n"
    "2000/4000/4000/12\n"
    "2500/5000/5000/12\n"
    "3000/6000/6000/8\n"
    "4000/8000/8000/8\n"
    "5000/10000/10000/8\n"
    "6000/12000/12000/8\n"
    "8000/16000/16000/8\n"
    "10000/20000/20000/6\n"
    "15000/25000/25000/6\n"
    "20000/30000/30000/6\n"
    "20000/40000/40000/6\n"
    "25000/50000/50000/6\n"
    "30000/60000/60000/6"
)


# UI 레이아웃을 정의하는 KV 언어 문자열입니다.
KV = """
Manager:
    SettingsScreen:
        name: 'settings'
    TimerScreen:
        name: 'timer'

<SettingsScreen>:
    on_pre_enter: app.build_blind_settings_ui()
    BoxLayout:
        orientation: 'vertical'
        padding: 20
        spacing: 10
        Label:
            text: 'Holdem Timer Settings'
            font_size: '32sp'
            size_hint_y: 0.1
        
        GridLayout:
            cols: 2
            size_hint_y: 0.2
            spacing: 10
            Label:
                text: 'Break After Levels (e.g., 5,10,15):'
            TextInput:
                id: break_levels_input
                text: '5, 10, 15, 20, 25'
            Label:
                text: 'Break Duration (minutes):'
            TextInput:
                id: break_duration_input
                text: '7'
                input_filter: 'int'
            Label:
                text: 'Level Up Sound:'
            BoxLayout:
                Label:
                    id: level_up_sound_label
                    text: app.get_filename(app.level_up_sound_path)
                Button:
                    text: '...'
                    size_hint_x: 0.2
                    on_press: app.choose_sound('level_up')
            Label:
                text: 'Break Start Sound:'
            BoxLayout:
                Label:
                    id: break_start_sound_label
                    text: app.get_filename(app.break_start_sound_path)
                Button:
                    text: '...'
                    size_hint_x: 0.2
                    on_press: app.choose_sound('break_start')
        
        BoxLayout:
            size_hint_y: 0.1
            spacing: 10
            Label:
                text: 'Set All Durations (min):'
            Spinner:
                id: all_duration_spinner
                text: '15'
                values: [str(i) for i in range(1, 61)]
            Button:
                text: 'Apply'
                on_press: app.set_all_durations(all_duration_spinner.text)

        GridLayout:
            cols: 6
            size_hint_y: 0.05
            Label:
                text: 'Level'
                bold: True
            Label:
                text: 'Small'
                bold: True
            Label:
                text: 'Big'
                bold: True
            Label:
                text: 'Ante'
                bold: True
            Label:
                text: 'Duration'
                bold: True
            Label:
                text: ''

        ScrollView:
            size_hint_y: 0.4
            GridLayout:
                id: blind_grid
                cols: 6
                size_hint_y: None
                height: self.minimum_height
                spacing: 5
                padding: 5
                
        Button:
            text: 'PLAY'
            font_size: '24sp'
            size_hint_y: 0.1
            on_press:
                app.setup_blinds(break_levels_input.text, break_duration_input.text)
                root.manager.current = 'timer'

<TimerScreen>:
    on_enter: app.start_scrolling_entrants()
    on_leave: app.stop_scrolling_entrants()
    BoxLayout:
        orientation: 'horizontal'
        # 왼쪽 패널
        BoxLayout:
            id: left_panel
            orientation: 'vertical'
            size_hint_x: 0.75
            padding: 10
            spacing: 2
            
            BoxLayout:
                orientation: 'vertical'
                spacing: -20
                size_hint_y: 0.13
                Label:
                    text: 'TOTAL TIME'
                Label:
                    id: total_time
                    text: app.total_time_str
                    font_size: '24sp'
                    bold: True

            BoxLayout:
                orientation: 'vertical'
                spacing: -18
                size_hint_y: 0.16
                Label:
                    text: 'TOTAL CHIPS'
                Label:
                    id: total_chips
                    text: app.total_chips_str
                    font_size: '24sp'
                    bold: True
                Label:
                    id: total_chips_bb
                    text: app.total_chips_bb_str
                    font_size: '16sp'
            
            BoxLayout:
                orientation: 'vertical'
                spacing: -18
                size_hint_y: 0.16
                Label:
                    text: 'AVR STACK'
                Label:
                    id: avr_stack
                    text: app.avr_stack_str
                    font_size: '24sp'
                    bold: True
                Label:
                    id: avr_stack_bb
                    text: app.avr_stack_bb_str
                    font_size: '16sp'

            BoxLayout:
                orientation: 'vertical'
                spacing: -20
                size_hint_y: 0.13
                Label:
                    text: 'PLAYERS'
                Label:
                    id: players
                    text: app.players_str
                    font_size: '24sp'
                    bold: True

            BoxLayout:
                orientation: 'vertical'
                spacing: -18
                size_hint_y: 0.16
                Label:
                    text: 'NEXT BREAK'
                Label:
                    id: next_break_time
                    text: app.next_break_time_str
                    font_size: '24sp'
                    bold: True
                Label:
                    id: next_break
                    text: app.next_break_str
                    font_size: '16sp'
            
            BoxLayout:
                orientation: 'vertical'
                spacing: -5
                size_hint_y: 0.26
                Label:
                    text: 'Prize'
                    bold: True
                GridLayout:
                    cols: 2
                    Label:
                        text: '1st:'
                        font_size: '18sp'
                    Label:
                        text: '0'
                    Label:
                        text: '2nd:'
                        font_size: '18sp'
                    Label:
                        text: '0'
                    Label:
                        text: '3rd:'
                        font_size: '18sp'
                    Label:
                        text: '0'
                    Label:
                        text: '4th:'
                        font_size: '18sp'
                    Label:
                        text: '0'
                    Label:
                        text: '5th:'
                        font_size: '18sp'
                    Label:
                        text: '0'


        # 중앙 패널
        BoxLayout:
            id: center_panel
            orientation: 'vertical'
            size_hint_x: 2.5
            padding: 20
            spacing: 5
            Label:
                id: level_label
                text: app.level_str
                font_size: '48sp'
                size_hint_y: 0.3
                color: app.level_label_color
            Label:
                id: timer_label
                text: app.level_time_str
                font_size: self.height * 0.8
                bold: True
                size_hint_y: 0.4
            Label:
                id: blinds_label
                text: app.blinds_str
                font_size: '40sp'
                size_hint_y: 0.2
                color: app.blinds_label_color
            Label:
                id: next_blinds_label
                text: app.next_blinds_str
                font_size: '20sp'
                color: 0.7, 0.7, 0.7, 1
                size_hint_y: 0.1

        # 오른쪽 패널
        BoxLayout:
            id: right_panel
            orientation: 'vertical'
            size_hint_x: 0.75
            padding: 10
            spacing: 5
            BoxLayout:
                size_hint_y: 0.075
                Button:
                    text: '<<'
                    on_press: app.prev_level()
                Button:
                    id: play_pause_button
                    text: '>' if app.is_paused else '||'
                    font_size: '32sp'
                    on_press: app.toggle_pause()
                Button:
                    text: '>>'
                    on_press: app.next_level()
            BoxLayout:
                size_hint_y: 0.05
                Button:
                    text: '+ 10s'
                    on_press: app.adjust_time(10)
                Button:
                    text: '- 10s'
                    on_press: app.adjust_time(-10)
            Slider:
                id: time_slider
                min: 0
                max: 1
                value: 1
                on_touch_move: app.seek_time(self.value)
                size_hint_y: 0.05
            
            BoxLayout:
                size_hint_y: 0.05
                Button:
                    text: '-'
                    on_press: app.adjust_players(-1)
                Label:
                    id: players_right
                    text: str(app.players)
                Button:
                    text: '+'
                    on_press: app.adjust_players(1)
            
            Label:
                text: 'CHIPS'
                size_hint_y: 0.05
            
            BoxLayout:
                orientation: 'horizontal'
                size_hint_y: 0.07
                spacing: 5
                Spinner:
                    id: chip_spinner
                    text: '1,000'
                    values: ['1,000', '3,000', '5,000', '10,000', '40,000', '50,000']
                    size_hint_x: 0.7
                Button:
                    text: 'OK'
                    size_hint_x: 0.3
                    on_press: app.add_selected_chips(chip_spinner.text)

            Button:
                text: 'HEADS-UP'
                size_hint_y: 0.08
                on_press: app.set_heads_up()
            Button:
                text: 'FINISH'
                size_hint_y: 0.08
                on_press:
                    app.reset_game()
                    root.manager.current = 'settings'
            
            Label:
                text: 'Entry'
                size_hint_y: 0.05
                bold: True
            
            ScrollView:
                id: entry_scroll
                bar_width: 0
                GridLayout:
                    id: entry_list
                    cols: 1
                    size_hint_y: None
                    height: self.minimum_height
                    spacing: 2
"""

class Manager(ScreenManager):
    pass

class SettingsScreen(Screen):
    pass

class TimerScreen(Screen):
    pass

class HoldemTimerApp(App):
    total_time = NumericProperty(0)
    level_time = NumericProperty(0)
    is_paused = BooleanProperty(True)
    time_to_next_break_seconds = NumericProperty(0)
    
    schedule = []
    current_schedule_index = NumericProperty(0)
    
    players = NumericProperty(0)
    total_players = NumericProperty(0)
    total_chips = NumericProperty(0)
    avr_stack = NumericProperty(0)
    entrants = ListProperty([])

    total_time_str = StringProperty("00:00:00")
    level_time_str = StringProperty("00:00")
    level_str = StringProperty("Level 1")
    blinds_str = StringProperty("Blinds: 0/0")
    next_blinds_str = StringProperty("Next: 0/0")
    next_break_str = StringProperty("...")
    next_break_time_str = StringProperty("00:00:00")
    total_chips_str = StringProperty("0")
    total_chips_bb_str = StringProperty("(0 BB)")
    avr_stack_str = StringProperty("0")
    avr_stack_bb_str = StringProperty("(0 BB)")
    players_str = StringProperty("0/0")
    
    sounds = {}
    
    level_up_sound_path = StringProperty("levelup.mp3")
    break_start_sound_path = StringProperty("break.mp3")
    _sound_to_update = StringProperty(None, allownone=True)
    scroll_event = ObjectProperty(None, allownone=True)
    blind_setting_widgets = ListProperty([])
    
    level_label_color = ListProperty([1, 1, 1, 1])
    blinds_label_color = ListProperty([1, 1, 1, 1])


    def build(self):
        self.title = 'Holdem Poker Timer'
        return Builder.load_string(KV)

    def build_blind_settings_ui(self):
        grid = self.root.get_screen('settings').ids.blind_grid
        if self.blind_setting_widgets:
            return
        grid.clear_widgets()
        self.blind_setting_widgets = []
        
        lines = DEFAULT_BLIND_STRUCTURE.strip().split('\n')

        for i, line in enumerate(lines):
            try:
                s, b, a, d = line.split('/')
            except ValueError:
                continue

            row_widgets = {}
            grid.add_widget(Label(text=str(i + 1), size_hint_y=None, height=40))
            
            small_input = TextInput(text=f"{int(s):,}", multiline=False, input_filter='int', size_hint_y=None, height=40)
            big_input = TextInput(text=f"{int(b):,}", multiline=False, input_filter='int', size_hint_y=None, height=40)
            ante_input = TextInput(text=f"{int(a):,}", multiline=False, input_filter='int', size_hint_y=None, height=40)
            duration_input = TextInput(text=d, multiline=False, input_filter='int', size_hint_y=None, height=40)
            
            small_input.bind(focus=self.format_text_input)
            big_input.bind(focus=self.format_text_input)
            ante_input.bind(focus=self.format_text_input)

            row_widgets['small'] = small_input
            row_widgets['big'] = big_input
            row_widgets['ante'] = ante_input
            row_widgets['duration'] = duration_input
            
            grid.add_widget(small_input)
            grid.add_widget(big_input)
            grid.add_widget(ante_input)
            grid.add_widget(duration_input)

            apply_button = Button(text='Apply Below', size_hint_y=None, height=40)
            apply_button.bind(on_press=partial(self.apply_duration_below, i))
            grid.add_widget(apply_button)
            
            self.blind_setting_widgets.append(row_widgets)

    def format_text_input(self, instance, is_focused):
        if not is_focused:
            try:
                num = int(instance.text.replace(',', ''))
                instance.text = f"{num:,}"
            except (ValueError, TypeError):
                instance.text = '0'

    def apply_duration_below(self, start_index, instance):
        try:
            duration_to_apply = self.blind_setting_widgets[start_index]['duration'].text
            for i in range(start_index + 1, len(self.blind_setting_widgets)):
                self.blind_setting_widgets[i]['duration'].text = duration_to_apply
        except IndexError:
            pass

    def set_all_durations(self, duration):
        for row in self.blind_setting_widgets:
            row['duration'].text = duration

    def on_start(self):
        Clock.schedule_once(lambda dt: self.build_blind_settings_ui())
        self.total_players = self.players
        self.total_chips = self.players * 40000
        self.update_avr_stack()

    def reset_game(self):
        self.is_paused = True
        Clock.unschedule(self.update)
        self.stop_scrolling_entrants()
        self.total_time = 0
        self.level_time = 0
        self.time_to_next_break_seconds = 0
        self.current_schedule_index = 0
        self.players = 0
        self.total_players = 0
        self.total_chips = 0
        self.schedule = []
        self.sounds = {}
        self.entrants = []
        self.update_ui()
        if self.root:
            timer_screen = self.root.get_screen('timer')
            if timer_screen:
                timer_screen.ids.play_pause_button.text = '>'

    def setup_blinds(self, break_levels_text, break_duration_text):
        self.schedule = []
        temp_blinds = []
        
        try:
            break_duration_seconds = int(break_duration_text.strip()) * 60
        except ValueError:
            break_duration_seconds = 420
            
        try:
            break_after_levels = {int(x.strip()) for x in break_levels_text.split(',')}
        except ValueError:
            break_after_levels = set()

        for i, row in enumerate(self.blind_setting_widgets):
            try:
                small = int(row['small'].text.replace(',', ''))
                big = int(row['big'].text.replace(',', ''))
                ante = int(row['ante'].text.replace(',', ''))
                duration = int(row['duration'].text)
                temp_blinds.append({'level': i + 1, 'small': small, 'big': big, 'ante': ante, 'duration': duration * 60})
            except (ValueError, KeyError):
                print(f"Skipping invalid blind format in row {i+1}")
                continue
        
        for i, level_info in enumerate(temp_blinds):
            self.schedule.append(level_info)
            if level_info['level'] in break_after_levels and i < len(temp_blinds) - 1:
                self.schedule.append({'is_break': True, 'level': 'Break', 'duration': break_duration_seconds})

        self.sounds = {}
        sound_files = {
            'level_up': self.level_up_sound_path,
            'break_start': self.break_start_sound_path
        }
        for key, path in sound_files.items():
            if path and os.path.exists(path):
                self.sounds[key] = SoundLoader.load(path)
                if not self.sounds[key]:
                    print(f"Error: Could not load sound file '{path}'")
            elif path:
                print(f"Warning: Sound file '{path}' not found.")

        self.current_schedule_index = 0
        self.reset_level_timer()
        self.calculate_time_to_next_break()
        self.update_ui()

    def choose_sound(self, sound_type):
        self._sound_to_update = sound_type
        filechooser.open_file(on_selection=self.handle_selection, filters=['*.wav', '*.mp3', '*.ogg'])

    def handle_selection(self, selection):
        if not selection:
            return

        path = selection[0]
        if self._sound_to_update == 'level_up':
            self.level_up_sound_path = path
        elif self._sound_to_update == 'break_start':
            self.break_start_sound_path = path
        
        self.root.get_screen('settings').ids.level_up_sound_label.text = self.get_filename(self.level_up_sound_path)
        self.root.get_screen('settings').ids.break_start_sound_label.text = self.get_filename(self.break_start_sound_path)


    def get_filename(self, path):
        if not path:
            return ''
        return os.path.basename(path)

    def play_sound(self, key):
        if key in self.sounds and self.sounds[key]:
            self.sounds[key].play()

    def start_timer(self):
        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        if self.is_paused:
            return
        self.level_time -= 1
        self.total_time += 1
        if self.time_to_next_break_seconds > 0:
            self.time_to_next_break_seconds -= 1
        if self.level_time <= 0:
            self.next_level()
        self.update_ui()

    def toggle_pause(self):
        self.is_paused = not self.is_paused
        if self.is_paused:
            Clock.unschedule(self.update)
        else:
            self.start_timer()
        self.root.get_screen('timer').ids.play_pause_button.text = '>' if self.is_paused else '||'

    def next_level(self):
        prev_item = self.get_current_schedule_item()
        if self.current_schedule_index < len(self.schedule) - 1:
            self.current_schedule_index += 1
            self.reset_level_timer()
            
            new_item = self.get_current_schedule_item()
            if new_item.get('is_break') and not prev_item.get('is_break'):
                self.play_sound('break_start')
            elif not new_item.get('is_break'):
                self.play_sound('level_up')
        else:
            self.is_paused = True
            
        self.calculate_time_to_next_break()
        self.update_ui()

    def prev_level(self):
        if self.current_schedule_index > 0:
            self.current_schedule_index -= 1
            self.reset_level_timer()
        self.calculate_time_to_next_break()
        self.update_ui()

    def reset_level_timer(self):
        current_item = self.get_current_schedule_item()
        self.level_time = current_item.get('duration', 600)
    
    def adjust_time(self, seconds):
        self.level_time += seconds
        if self.level_time < 0:
            self.level_time = 0
        self.calculate_time_to_next_break()
        self.update_ui()

    def seek_time(self, value):
        current_item = self.get_current_schedule_item()
        duration = current_item.get('duration', 1)
        self.level_time = duration * (1 - value)
        self.calculate_time_to_next_break()
        self.update_ui()

    def get_current_schedule_item(self):
        if not self.schedule or self.current_schedule_index >= len(self.schedule):
             return {'level': 1, 'small': 0, 'big': 0, 'ante': 0, 'duration': 600}
        return self.schedule[self.current_schedule_index]

    def get_next_blinds_info(self):
        for i in range(self.current_schedule_index + 1, len(self.schedule)):
            if not self.schedule[i].get('is_break'):
                return self.schedule[i]
        return None

    def calculate_time_to_next_break(self):
        current_item = self.get_current_schedule_item()
        if not self.schedule or current_item.get('is_break'):
            self.time_to_next_break_seconds = 0
            return

        time_left = self.level_time
        for i in range(self.current_schedule_index + 1, len(self.schedule)):
            next_item = self.schedule[i]
            if next_item.get('is_break'):
                self.time_to_next_break_seconds = time_left
                return
            else:
                time_left += next_item.get('duration', 0)
        
        self.time_to_next_break_seconds = 0

    def update_ui(self):
        self.total_time_str = self.format_time(self.total_time, with_hours=True)
        self.level_time_str = self.format_time(self.level_time)
        self.next_break_time_str = self.format_time(self.time_to_next_break_seconds, with_hours=True)

        current_item = self.get_current_schedule_item()
        if current_item.get('is_break'):
            self.level_str = "BREAK"
            self.blinds_str = "Tournament is paused"
            self.level_label_color = [1, 1, 0, 1]
            self.blinds_label_color = [1, 0, 0, 1]
            self.next_break_str = "Now Break"
        else:
            level = current_item.get('level', 1)
            small = current_item.get('small', 0)
            big = current_item.get('big', 0)
            ante = current_item.get('ante', 0)
            self.level_str = f"Level {level}"
            ante_str = f" / {ante:,}" if ante > 0 else ""
            self.blinds_str = f"Blinds: {small:,} / {big:,}{ante_str}"
            self.level_label_color = [1, 1, 1, 1]
            self.blinds_label_color = [1, 1, 1, 1]

            levels_left = 0
            found_break = False
            for item in self.schedule[self.current_schedule_index:]:
                if item.get('is_break'):
                    found_break = True
                    break
                if not item.get('is_break'):
                    levels_left += 1
            
            if found_break:
                 self.next_break_str = f"{levels_left} level(s) left"
            else:
                 self.next_break_str = "No more breaks"

        next_blinds = self.get_next_blinds_info()
        if next_blinds:
            level = next_blinds.get('level', 1)
            small = next_blinds.get('small', 0)
            big = next_blinds.get('big', 0)
            ante = next_blinds.get('ante', 0)
            ante_str = f" / {ante:,}" if ante > 0 else ""
            self.next_blinds_str = f"Next Level {level}: {small:,} / {big:,}{ante_str}"
        else:
            self.next_blinds_str = "Last Level"

        self.total_chips_str = f"{self.total_chips:,}"
        self.avr_stack_str = f"{self.avr_stack:,}"
        self.players_str = f"{self.players}/{self.total_players}"

        big_blind = 0
        if current_item.get('is_break'):
            if self.current_schedule_index > 0:
                prev_level_info = self.schedule[self.current_schedule_index - 1]
                big_blind = prev_level_info.get('big', 0)
        else:
            big_blind = current_item.get('big', 0)

        if big_blind > 0:
            total_chips_bb = round(self.total_chips / big_blind, 1)
            avr_stack_bb = round(self.avr_stack / big_blind, 1)
            self.total_chips_bb_str = f"({total_chips_bb} BB)"
            self.avr_stack_bb_str = f"({avr_stack_bb} BB)"
        else:
            self.total_chips_bb_str = "(0 BB)"
            self.avr_stack_bb_str = "(0 BB)"

        duration = current_item.get('duration', 1)
        if duration > 0:
            self.root.get_screen('timer').ids.time_slider.value = 1 - (self.level_time / duration)

    def format_time(self, seconds, with_hours=False):
        m, s = divmod(int(seconds), 60)
        h, m = divmod(m, 60)
        if with_hours:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

    def add_chips(self, amount):
        self.total_chips += amount
        self.update_avr_stack()

    def add_selected_chips(self, amount_str):
        try:
            amount = int(amount_str.replace(',', ''))
            self.add_chips(amount)
        except ValueError:
            print(f"Invalid chip amount selected: {amount_str}")

    def adjust_players(self, amount):
        if amount > 0:
            self.players += 1
            self.total_players += 1
            self.total_chips += 40000
            self.entrants.append(f"Guest_{self.total_players}")
        elif amount < 0:
            if self.players > 1:
                self.players -= 1
        self.update_avr_stack()

    def update_avr_stack(self):
        if self.players > 0:
            self.avr_stack = math.ceil(self.total_chips / self.players)
        else:
            self.avr_stack = 0
        self.update_ui()
    
    def set_heads_up(self):
        if self.total_players >= 2:
            self.players = 2

            for i in range(self.current_schedule_index + 1, len(self.schedule)):
                if not self.schedule[i].get('is_break'):
                    self.schedule[i]['duration'] = 300
            
            self.calculate_time_to_next_break()
            self.update_avr_stack()
    
    def start_scrolling_entrants(self):
        self.stop_scrolling_entrants()
        self.scroll_event = Clock.schedule_interval(self.scroll_entrants, 1 / 60.)

    def stop_scrolling_entrants(self):
        if self.scroll_event:
            self.scroll_event.cancel()
            self.scroll_event = None

    def scroll_entrants(self, dt):
        timer_screen = self.root.get_screen('timer')
        sv = timer_screen.ids.entry_scroll
        grid = timer_screen.ids.entry_list

        if grid.height > sv.height:
            sv.scroll_y -= 0.0005

            if sv.scroll_y <= 0:
                sv.scroll_y = 1
        else:
            self.stop_scrolling_entrants()
    
    def check_scroll_necessity(self, dt):
        timer_screen = self.root.get_screen('timer')
        sv = timer_screen.ids.entry_scroll
        grid = timer_screen.ids.entry_list
        if grid.height > sv.height:
            self.start_scrolling_entrants()
        else:
            self.stop_scrolling_entrants()

    def on_entrants(self, instance, value):
        entry_grid = self.root.get_screen('timer').ids.entry_list
        entry_grid.clear_widgets()
        for name in value:
            entry_grid.add_widget(Label(text=name, size_hint_y=None, height=60, font_size='24sp'))
        Clock.schedule_once(self.check_scroll_necessity, 0.1)

    def on_players(self, instance, value):
        self.root.get_screen('timer').ids.players_right.text = str(value)
        self.update_ui()

    def on_total_chips(self, instance, value):
        self.update_avr_stack()

    def on_avr_stack(self, instance, value):
        self.update_ui()

if __name__ == '__main__':
    HoldemTimerApp().run()
