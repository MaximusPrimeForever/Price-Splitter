"""Splitter GUI."""
import sys

import argparse
from typing import Dict, List

from dataclasses import dataclass
from PyQt5.QtGui import QPalette, QColor

from PyQt5.QtWidgets import (QApplication, QCheckBox, QComboBox,
                             QGridLayout, QLabel, QLineEdit,
                             QPushButton, QWidget)

DUPLICATE_PRICE_DEL = " ("
CURRENT_ENTRY_ID = "Current"


@dataclass
class CheckboxAndPrice:
    """Wrapper for checkbox and QlineEdit."""

    checkbox: QCheckBox
    price: QLineEdit


@dataclass
class HistoryItem:
    """Save the checkbox and QLineEdit state for history."""

    is_participating: bool
    price_share: float


@dataclass
class Participant:
    """Container for each participant's data."""

    name: str
    total_share: float
    ui: CheckboxAndPrice


class SplitterUI(QWidget):
    """Splitter GUI class."""

    def __init__(self, participants: List[str], use_light_theme: bool):
        """Initialize UI."""
        super().__init__()
        self.grid_layout = QGridLayout()

        self.setWindowTitle("Splitter")

        self.product_price_box = QLineEdit()
        self.product_price_box.setPlaceholderText("Product price..")
        self.product_price_box.returnPressed.connect(self._add_entry)

        # history is a dictionary using product prices as keys
        # the values are the people in the transaction and
        # their respective shares
        self.history: Dict[str, Dict[str, HistoryItem]] = {}

        self.participants: Dict[str, Participant] = {}
        for p in participants:
            self.participants[p] = Participant(
                p,
                0,
                CheckboxAndPrice(QCheckBox(p), QLineEdit("0"))
            )
            self.participants[p].ui.price.setReadOnly(True)

        # * add and clear buttons
        self.add_button = QPushButton("Add to total")
        self.add_button.clicked.connect(self._add_entry)

        self.clear_button = QPushButton("Clear entry")
        self.clear_button.clicked.connect(self._clear_entry)

        self.total_price: float = 0
        self.total_price_line_edit = QLineEdit(str(self.total_price))
        self.total_price_line_edit.setReadOnly(True)

        self.history_combobox = QComboBox()
        self.history_combobox.currentIndexChanged.connect(
            self._load_state_from_combobox
        )
        self.history_combobox.addItem(CURRENT_ENTRY_ID)

        if use_light_theme:
            self._set_light_theme()
        else:
            self._set_dark_theme()

        self._build_grid(spacing=5)

    def _set_dark_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(53, 53, 53))
        palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        palette.setColor(QPalette.Base, QColor(25, 25, 25))
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        palette.setColor(QPalette.Text, QColor(255, 255, 255))
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        self.setPalette(palette)

    def _set_light_theme(self):
        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(230, 230, 230))
        palette.setColor(QPalette.WindowText, QColor(10, 10, 10))
        palette.setColor(QPalette.Base, QColor(230, 230, 230))
        palette.setColor(QPalette.AlternateBase, QColor(230, 230, 230))
        palette.setColor(QPalette.ToolTipBase, QColor(0, 0, 0))
        palette.setColor(QPalette.ToolTipText, QColor(10, 10, 10))
        palette.setColor(QPalette.Text, QColor(10, 10, 10))
        palette.setColor(QPalette.Button, QColor(230, 230, 230))
        palette.setColor(QPalette.ButtonText, QColor(10, 10, 10))
        palette.setColor(QPalette.BrightText, QColor(10, 0, 0))
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))

        self.setPalette(palette)

    def _build_grid(self, spacing: int = 5):
        # add top product price box, and history dropdown
        self.grid_line_count = 1
        self.grid_layout.addWidget(self.product_price_box, 1, 0)
        self.grid_layout.addWidget(self.history_combobox, 1, 1)
        self.grid_line_count += 1

        # add participiants widgets - checbox, and share of the price
        for _, p_data in self.participants.items():
            self.grid_layout.addWidget(
                p_data.ui.checkbox,
                self.grid_line_count,
                0
            )
            self.grid_layout.addWidget(
                p_data.ui.price,
                self.grid_line_count,
                1
            )

            self.grid_line_count += 1

        # add 'add' and 'clear' buttons
        self.grid_layout.addWidget(self.add_button, self.grid_line_count, 0)
        self.grid_layout.addWidget(self.clear_button, self.grid_line_count, 1)
        self.grid_line_count += 1

        # add total price accumulator
        self.grid_layout.addWidget(QLabel("Total:"), self.grid_line_count, 0)
        self.grid_layout.addWidget(self.total_price_line_edit, self.grid_line_count, 1)
        self.grid_line_count += 1

        self.grid_layout.setSpacing(spacing)
        self.setLayout(self.grid_layout)

    def _clear_entry(self):
        """Clear current entry."""
        if len(self.history_combobox) == 0:
            print("no entries to remove")
            return

        if self.history_combobox.currentText() == CURRENT_ENTRY_ID:
            print("Will not delete Current entry.")
            return

        # get price of product and split it
        current_price_str = self.history_combobox.currentText()
        current_price = float(current_price_str.split(DUPLICATE_PRICE_DEL)[0])

        history_item = self.history[current_price_str]
        split_price = self._split_price(current_price, from_history_item=history_item)

        # subtract cost from total price
        self.total_price -= current_price
        self.total_price_line_edit.setText(str(self.total_price))

        # subtract cost from each participant's share
        # check if participating from history data, not UI
        for p_name, p_data in self.participants.items():
            if history_item[p_name].is_participating:
                p_data.total_share -= split_price
                p_data.ui.price.setText(
                    str(p_data.total_share)
                )

        # load the previous entry if it exists
        item_index = self.history_combobox.currentIndex()

        # remove current item, and focus on the product price
        del(self.history[current_price_str])
        self.history_combobox.removeItem(item_index)

        if len(self.history_combobox) == 1:
            self.product_price_box.setText("")

            for _, p_data in self.participants.items():
                p_data.total_share = 0
                p_data.ui.price.setText(str(p_data.total_share))
                p_data.ui.checkbox.setChecked(False)

        self.product_price_box.setFocus()

    def _add_entry(self):
        """Compute the product price per person, and update text boxes."""
        if not self.product_price_box.text():
            return

        # get the product price from GUI
        product_price = 0.0
        try:
            product_price = float(self.product_price_box.text())
        except ValueError as e:
            self.product_price_box.clear()
            print(e)
            return

        # divide the product price for all participants
        try:
            price_for_each = self._split_price(product_price)
        except ValueError as e:
            print(e)
            return

        # add the partial cost to each participant
        for _, p_data in self.participants.items():
            # only update the price if the person participates
            if p_data.ui.checkbox.isChecked():
                p_data.total_share += price_for_each
                p_data.ui.price.setText(str(p_data.total_share))

        # update total price
        self.total_price += product_price
        self.total_price_line_edit.setText(str(self.total_price))

        self.product_price_box.setText("")
        self.product_price_box.setFocus()
        self.product_price_box.setText("")

        history_key = self._save_state_to_history(str(product_price))
        self.history_combobox.setCurrentText(history_key)

    def _serialize_current_price(self):
        """Serialize current state as a single history item."""
        current_participations: Dict[str, HistoryItem] = {}

        for p_name, p_data in self.participants.items():
            current_participations[p_name] = HistoryItem(
                p_data.ui.checkbox.isChecked(),
                float(p_data.ui.price.text()),
            )

        return current_participations

    def _save_state_to_history(self, product_price: str):
        """Save current state to history."""
        current_state = self._serialize_current_price()
        # TODO: handle duplicates

        duplicates = []
        # check if there is already an entry with the same price
        for key in self.history:
            split_key = key.split(DUPLICATE_PRICE_DEL)

            # find the maximum duplicate
            if split_key[0] == product_price:
                duplicates.append(split_key)

        if len(duplicates) == 0:
            final_key = product_price
        else:
            last_duplicate = duplicates[-1]
            if len(last_duplicate) == 1:
                final_key = f"{product_price} (1)"
            elif len(last_duplicate) > 1:
                duplicate_counter = int(last_duplicate[1][:-1])
                final_key = f"{product_price} ({duplicate_counter + 1})"

        self.history[final_key] = current_state
        self.history_combobox.addItem(final_key)

        return final_key

    def _load_state_from_history(self, product_price: str):
        """Load a state from history into UI.

        Overwrite values in text boxes.
        """
        if len(self.history) == 0:
            print("history is empty")
            return

        # if the `Current` entry is selected, update the UI with
        # the current values and quit
        if product_price == CURRENT_ENTRY_ID:
            for _, p_data in self.participants.items():
                p_data.ui.checkbox.setChecked(False)
                p_data.ui.price.setText(
                    str(p_data.total_share)
                )
            return

        state: Dict[str, HistoryItem] = self.history[product_price]

        # set the checkboxes and LineEdits with participation and shares
        for person in state:
            # set checkbox state
            self.participants[person].ui.checkbox.setChecked(
                state[person].is_participating
            )

            # set price in QLineEdit
            self.participants[person].ui.price.setText(
                str(state[person].price_share)
            )

        self.product_price_box.setText(product_price.split(DUPLICATE_PRICE_DEL)[0])

    def _load_state_from_combobox(self, _):
        """Load state from history when selected from the history combobox."""
        self._load_state_from_history(
            self.history_combobox.currentText()
        )

    def _split_price(self,
                     product_price: float,
                     from_history_item: Dict[str, HistoryItem] = None):
        """Count the participants in the price, and split `product_price` accordingly."""
        active_people = 0

        # if price should be split using history data or UI data
        if from_history_item is not None:
            for _, person_history_data in from_history_item.items():
                if person_history_data.is_participating:
                    active_people += 1
        else:
            for _, p_data in self.participants.items():
                if p_data.ui.checkbox.isChecked():
                    active_people += 1

        if active_people == 0:
            raise ValueError("No participants in price")

        return product_price / active_people


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Pre-splitwise splitter.")
    parser.add_argument(
        'participants',
        type=str,
        nargs='+',
        help="List of participants."
    )
    parser.add_argument(
        '--light_theme',
        action=argparse.BooleanOptionalAction,
        type=bool,
        help="include to enable light theme."
    )
    args = parser.parse_args()
    if len(args.participants) < 1:
        print("Supply at least one participant.")
        sys.exit(-1)

    app = QApplication([])
    app.setStyle('Fusion')

    gallery = SplitterUI(args.participants, args.light_theme)
    gallery.show()

    app.exec()
