import os
import re

from PySide6.QtCore import QThread, Signal, Qt, QTimer
from PySide6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QPushButton,
    QScrollArea,
    QSizePolicy,
    QTextBrowser,
    QVBoxLayout,
    QWidget,
)

from ollama_client import ask_pravithai
from chat_storage import (
    delete_chat,
    list_chats,
    load_chat,
    save_chat,
)


def clean_response(text: str) -> str:
    """
    Clean formatting after enough of the response has been received
    to give the formatter proper context.
    """

    text = text.replace("$$", "")
    text = text.replace("\\[", "")
    text = text.replace("\\]", "")
    text = text.replace("\\(", "")
    text = text.replace("\\)", "")

    replacements = {
        "\\times": "×",
        "\\cdot": "·",
        "\\div": "÷",
        "\\leq": "≤",
        "\\geq": "≥",
        "\\neq": "≠",
        "\\pm": "±",
        "\\pi": "π",
    }

    for old, new in replacements.items():
        text = text.replace(old, new)

    text = re.sub(
        r"\\frac\s*\{([^{}]*)\}\s*\{([^{}]*)\}",
        r"\1/\2",
        text,
    )

    text = re.sub(
        r"\\sqrt\s*\{([^{}]*)\}",
        r"√(\1)",
        text,
    )

    text = re.sub(
        r"\\boxed\s*\{([^{}]*)\}",
        r"\1",
        text,
    )

    text = text.replace("$", "")

    text = re.sub(
        r"^\s*---+\s*$",
        "",
        text,
        flags=re.MULTILINE,
    )

    text = re.sub(
        r"\bStep\s*(\d+)\s*:",
        r"Step \1:",
        text,
        flags=re.IGNORECASE,
    )

    text = re.sub(
        r"(?<!^)(Step \d+:)",
        r"\n\n\1",
        text,
    )

    text = re.sub(
        r"([.!?])([A-Za-z0-9])",
        r"\1 \2",
        text,
    )

    text = re.sub(
        r":([A-Za-z0-9])",
        r": \1",
        text,
    )

    text = re.sub(
        r"\s*([×÷−=])\s*",
        r" \1 ",
        text,
    )

    text = re.sub(
        r"(\d)\s+x\b",
        r"\1x",
        text,
    )

    text = "\n".join(
        line.strip()
        for line in text.splitlines()
    )

    text = re.sub(
        r"[ \t]{2,}",
        " ",
        text,
    )

    text = re.sub(
        r"\n{3,}",
        "\n\n",
        text,
    )

    return text.strip()


class AIWorker(QThread):
    token_received = Signal(str)
    finished_response = Signal()
    error = Signal(str)

    def __init__(
        self,
        message,
        image_path=None,
        history=None,
    ):
        super().__init__()

        self.message = message
        self.image_path = image_path
        self.history = history or []

    def run(self):
        try:
            for token in ask_pravithai(
                self.message,
                self.image_path,
                self.history,
            ):
                self.token_received.emit(token)

            self.finished_response.emit()

        except Exception as e:
            self.error.emit(str(e))


class MessageBubble(QWidget):
    def __init__(
        self,
        sender,
        text="",
        is_user=False,
    ):
        super().__init__()

        self.is_user = is_user
        self.streaming = False

        layout = QVBoxLayout(self)

        layout.setContentsMargins(
            14,
            10,
            14,
            10,
        )

        layout.setSpacing(4)

        self.sender_label = QLabel(sender)

        self.sender_label.setStyleSheet(
            """
            QLabel {
                font-size: 13px;
                font-weight: bold;
                color: #89b4fa;
                background: transparent;
            }
            """
        )

        self.message = QTextBrowser()

        self.message.setReadOnly(True)
        self.message.setOpenExternalLinks(True)

        self.message.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Fixed,
        )

        self.message.setVerticalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.message.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.message.setStyleSheet(
            """
            QTextBrowser {
                background: transparent;
                border: none;
                padding: 0px;
                color: #cdd6f4;
                selection-background-color: #585b70;
                selection-color: #ffffff;
            }
            """
        )

        layout.addWidget(
            self.sender_label
        )

        layout.addWidget(
            self.message
        )

        if is_user:
            self.setStyleSheet(
                """
                QWidget {
                    background: #313244;
                    border-radius: 12px;
                }
                """
            )

            self.sender_label.setStyleSheet(
                """
                QLabel {
                    font-size: 13px;
                    font-weight: bold;
                    color: #cba6f7;
                    background: transparent;
                }
                """
            )

        else:
            self.setStyleSheet(
                """
                QWidget {
                    background: #1e1e2e;
                    border-radius: 12px;
                }
                """
            )

        self.set_text(text)
        self.finalize_size()

    def set_text(self, text):
        self.message.setPlainText(text)

    def begin_streaming(self):
        self.streaming = True

        self.message.setFixedHeight(
            55
        )

    def finalize_size(self):
        self.streaming = False

        document = self.message.document()

        document.adjustSize()

        height = int(
            document.size().height()
        ) + 12

        self.message.setFixedHeight(
            max(36, height)
        )

        self.adjustSize()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(
            "PravithAI"
        )

        self.resize(
            900,
            650,
        )

        self.worker = None
        self.current_ai_bubble = None

        self.current_response = ""
        self.displayed_response = ""

        self.attached_image = None

        # Conversation memory
        self.conversation = []

        # Saved chat information
        self.current_chat_title = None

        self.stream_timer = QTimer(self)

        self.stream_timer.setInterval(
            60
        )

        self.stream_timer.timeout.connect(
            self.update_stream_display
        )

        self.setStyleSheet(
            """
            QMainWindow {
                background: #11111b;
            }

            QWidget {
                color: #cdd6f4;
                font-family: "JetBrains Mono";
                font-size: 14px;
            }

            QScrollArea {
                border: none;
                background: #11111b;
            }

            QLineEdit {
                background: #1e1e2e;
                border: 1px solid #45475a;
                border-radius: 10px;
                padding: 12px;
                color: #cdd6f4;
                selection-background-color: #585b70;
            }

            QLineEdit:focus {
                border: 1px solid #89b4fa;
            }

            QPushButton {
                background: #89b4fa;
                color: #11111b;
                border: none;
                border-radius: 10px;
                padding: 12px 18px;
                font-weight: bold;
            }

            QPushButton:hover {
                background: #b4befe;
            }

            QPushButton:pressed {
                background: #74c7ec;
            }

            QPushButton:disabled {
                background: #45475a;
                color: #6c7086;
            }

            QLabel#attachment_label {
                background: #1e1e2e;
                color: #89b4fa;
                border: 1px solid #45475a;
                border-radius: 8px;
                padding: 6px 10px;
            }
            """
        )

        central = QWidget()

        self.setCentralWidget(
            central
        )

        main_layout = QVBoxLayout(
            central
        )

        main_layout.setContentsMargins(
            18,
            18,
            18,
            18,
        )

        main_layout.setSpacing(12)

        # -------------------------
        # HEADER
        # -------------------------

        header_layout = QHBoxLayout()

        header = QLabel(
            "PravithAI"
        )

        header.setStyleSheet(
            """
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #cdd6f4;
                padding: 4px;
                background: transparent;
            }
            """
        )

        subtitle = QLabel(
            "Local AI • Qwen3 1.7B"
        )

        subtitle.setStyleSheet(
            """
            QLabel {
                font-size: 12px;
                color: #6c7086;
                padding-left: 5px;
                background: transparent;
            }
            """
        )

        self.new_chat_button = QPushButton(
            "＋ New Chat"
        )

        self.new_chat_button.clicked.connect(
            self.new_chat
        )

        self.saved_chats_button = QPushButton(
            "💾 Saved"
        )

        self.saved_chats_button.clicked.connect(
            self.show_saved_chats
        )

        header_text = QVBoxLayout()

        header_text.addWidget(
            header
        )

        header_text.addWidget(
            subtitle
        )

        header_layout.addLayout(
            header_text,
            1,
        )

        header_layout.addWidget(
            self.saved_chats_button
        )

        header_layout.addWidget(
            self.new_chat_button
        )

        main_layout.addLayout(
            header_layout
        )

        # -------------------------
        # CHAT
        # -------------------------

        self.scroll = QScrollArea()

        self.scroll.setWidgetResizable(
            True
        )

        self.scroll.setHorizontalScrollBarPolicy(
            Qt.ScrollBarPolicy.ScrollBarAlwaysOff
        )

        self.chat_container = QWidget()

        self.chat_layout = QVBoxLayout(
            self.chat_container
        )

        self.chat_layout.setContentsMargins(
            8,
            8,
            8,
            8,
        )

        self.chat_layout.setSpacing(
            10
        )

        self.chat_layout.addStretch()

        self.scroll.setWidget(
            self.chat_container
        )

        main_layout.addWidget(
            self.scroll,
            1,
        )

        # -------------------------
        # ATTACHMENT
        # -------------------------

        self.attachment_label = QLabel()

        self.attachment_label.setObjectName(
            "attachment_label"
        )

        self.attachment_label.setVisible(
            False
        )

        main_layout.addWidget(
            self.attachment_label
        )

        # -------------------------
        # INPUT
        # -------------------------

        input_layout = QHBoxLayout()

        input_layout.setSpacing(8)

        self.attach_button = QPushButton(
            "📎"
        )

        self.attach_button.setToolTip(
            "Attach an image"
        )

        self.attach_button.setFixedWidth(
            48
        )

        self.attach_button.clicked.connect(
            self.choose_image
        )

        input_layout.addWidget(
            self.attach_button
        )

        self.input = QLineEdit()

        self.input.setPlaceholderText(
            "Ask PravithAI anything..."
        )

        self.input.returnPressed.connect(
            self.send_message
        )

        self.send_button = QPushButton(
            "Send"
        )

        self.send_button.clicked.connect(
            self.send_message
        )

        input_layout.addWidget(
            self.input,
            1,
        )

        input_layout.addWidget(
            self.send_button
        )

        main_layout.addLayout(
            input_layout
        )

        # -------------------------
        # WELCOME
        # -------------------------

        self.show_welcome()

    # -------------------------
    # WELCOME
    # -------------------------

    def show_welcome(self):
        welcome = MessageBubble(
            "PravithAI",
            "Hey! 👋 I'm ready. Ask me something.",
            False,
        )

        self.add_message(
            welcome
        )

    # -------------------------
    # CHOOSE IMAGE
    # -------------------------

    def choose_image(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Choose an image",
            "",
            "Images (*.png *.jpg *.jpeg *.webp *.bmp)",
        )

        if not file_path:
            return

        if not os.path.isfile(
            file_path
        ):
            return

        self.attached_image = file_path

        filename = os.path.basename(
            file_path
        )

        self.attachment_label.setText(
            f"📎 {filename}"
        )

        self.attachment_label.setVisible(
            True
        )

        self.input.setFocus()

    # -------------------------
    # CLEAR IMAGE
    # -------------------------

    def clear_attachment(self):
        self.attached_image = None

        self.attachment_label.clear()

        self.attachment_label.setVisible(
            False
        )

    # -------------------------
    # ADD MESSAGE
    # -------------------------

    def add_message(self, widget):
        self.chat_layout.insertWidget(
            self.chat_layout.count() - 1,
            widget,
        )

        self.scroll_to_bottom()

    # -------------------------
    # CLEAR CHAT UI
    # -------------------------

    def clear_chat_ui(self):
        while (
            self.chat_layout.count()
            > 1
        ):
            item = (
                self.chat_layout.takeAt(0)
            )

            widget = item.widget()

            if widget:
                widget.deleteLater()

    # -------------------------
    # SCROLL
    # -------------------------

    def is_at_bottom(self):
        scrollbar = (
            self.scroll.verticalScrollBar()
        )

        return (
            scrollbar.value()
            >= scrollbar.maximum() - 20
        )

    def scroll_to_bottom(self):
        scrollbar = (
            self.scroll.verticalScrollBar()
        )

        scrollbar.setValue(
            scrollbar.maximum()
        )

    # -------------------------
    # SEND
    # -------------------------

    def send_message(self):
        message = (
            self.input.text().strip()
        )

        image_path = (
            self.attached_image
        )

        if (
            not message
            and not image_path
        ):
            return

        if (
            self.worker is not None
            and self.worker.isRunning()
        ):
            return

        self.input.clear()

        if image_path:
            filename = os.path.basename(
                image_path
            )

            if message:
                display_message = (
                    f"📎 {filename}\n\n"
                    f"{message}"
                )
            else:
                display_message = (
                    f"📎 {filename}\n\n"
                    "Describe this image."
                )

        else:
            display_message = message

        user_bubble = MessageBubble(
            "You",
            display_message,
            True,
        )

        self.add_message(
            user_bubble
        )

        # Keep the conversation history
        user_history_message = {
            "role": "user",
            "content": message,
        }

        if image_path:
            user_history_message[
                "images"
            ] = [image_path]

        # Save this message temporarily.
        self.conversation.append(
            user_history_message
        )

        self.clear_attachment()

        self.current_response = ""
        self.displayed_response = ""

        self.current_ai_bubble = MessageBubble(
            "PravithAI",
            "Thinking...",
            False,
        )

        self.current_ai_bubble.begin_streaming()

        self.add_message(
            self.current_ai_bubble
        )

        self.input.setEnabled(False)
        self.send_button.setEnabled(False)
        self.attach_button.setEnabled(False)
        self.new_chat_button.setEnabled(False)
        self.saved_chats_button.setEnabled(False)

        # Don't include the newest user message
        # twice. The worker adds it itself.
        history = self.conversation[:-1]

        self.worker = AIWorker(
            message,
            image_path,
            history,
        )

        self.worker.token_received.connect(
            self.receive_token
        )

        self.worker.finished_response.connect(
            self.response_finished
        )

        self.worker.error.connect(
            self.response_error
        )

        self.worker.start()

        self.stream_timer.start()

    # -------------------------
    # RECEIVE TOKEN
    # -------------------------

    def receive_token(self, token):
        self.current_response += token

    # -------------------------
    # UPDATE STREAM
    # -------------------------

    def update_stream_display(self):
        if (
            self.current_ai_bubble
            is None
        ):
            return

        if not self.current_response:
            return

        if (
            self.displayed_response
            == self.current_response
        ):
            return

        should_follow = (
            self.is_at_bottom()
        )

        cleaned = clean_response(
            self.current_response
        )

        if not cleaned:
            return

        self.displayed_response = (
            self.current_response
        )

        self.current_ai_bubble.set_text(
            cleaned
        )

        if should_follow:
            self.scroll_to_bottom()

    # -------------------------
    # FINISHED
    # -------------------------

    def response_finished(self):
        self.stream_timer.stop()

        final_text = clean_response(
            self.current_response
        )

        if self.current_ai_bubble:
            self.current_ai_bubble.set_text(
                final_text
            )

            self.current_ai_bubble.finalize_size()

        # Add AI response to memory
        self.conversation.append(
            {
                "role": "assistant",
                "content": final_text,
            }
        )

        self.input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.attach_button.setEnabled(True)
        self.new_chat_button.setEnabled(True)
        self.saved_chats_button.setEnabled(True)

        self.input.setFocus()

        if self.worker:
            self.worker.deleteLater()
            self.worker = None

        self.current_ai_bubble = None
        self.current_response = ""
        self.displayed_response = ""

        self.scroll_to_bottom()

    # -------------------------
    # ERROR
    # -------------------------

    def response_error(
        self,
        error_message,
    ):
        self.stream_timer.stop()

        if self.current_ai_bubble:
            self.current_ai_bubble.set_text(
                f"Error: {error_message}"
            )

            self.current_ai_bubble.finalize_size()

        # Remove the user message from
        # memory because it didn't get
        # a valid AI response.
        if self.conversation:
            self.conversation.pop()

        self.input.setEnabled(True)
        self.send_button.setEnabled(True)
        self.attach_button.setEnabled(True)
        self.new_chat_button.setEnabled(True)
        self.saved_chats_button.setEnabled(True)

        self.input.setFocus()

        if self.worker:
            self.worker.deleteLater()
            self.worker = None

        self.current_ai_bubble = None
        self.current_response = ""
        self.displayed_response = ""

        self.scroll_to_bottom()

    # -------------------------
    # NEW CHAT
    # -------------------------

    def new_chat(self):
        if (
            self.worker is not None
            and self.worker.isRunning()
        ):
            return

        if self.conversation:
            self.save_current_chat()

        self.conversation = []
        self.current_chat_title = None

        self.clear_attachment()
        self.clear_chat_ui()

        self.show_welcome()

        self.input.setFocus()

    # -------------------------
    # SAVE CURRENT CHAT
    # -------------------------

    def save_current_chat(self):
        if not self.conversation:
            return

        first_message = None

        for message in self.conversation:
            if (
                message["role"]
                == "user"
                and message.get("content")
            ):
                first_message = (
                    message["content"]
                )
                break

        if first_message:
            title = (
                first_message
                .replace("\n", " ")
                .strip()
            )[:60]
        else:
            title = "Untitled Chat"

        try:
            save_chat(
                title,
                self.conversation,
            )

            self.current_chat_title = (
                title
            )

        except Exception as e:
            print(
                f"Could not save chat: {e}"
            )

    # -------------------------
    # SHOW SAVED CHATS
    # -------------------------

    def show_saved_chats(self):
        if (
            self.worker is not None
            and self.worker.isRunning()
        ):
            return

        chats = list_chats()

        if not chats:
            self.saved_chats_button.setText(
                "💾 No Saved Chats"
            )

            QTimer.singleShot(
                1500,
                lambda: self.saved_chats_button.setText(
                    "💾 Saved"
                ),
            )

            return

        self.saved_window = QWidget(
            self,
            Qt.WindowType.Window,
        )

        self.saved_window.setWindowTitle(
            "Saved Chats"
        )

        self.saved_window.resize(
            500,
            450,
        )

        layout = QVBoxLayout(
            self.saved_window
        )

        label = QLabel(
            "💾 Saved Conversations"
        )

        label.setStyleSheet(
            """
            QLabel {
                font-size: 18px;
                font-weight: bold;
                color: #cdd6f4;
            }
            """
        )

        layout.addWidget(
            label
        )

        self.saved_list = QListWidget()

        for chat in chats:
            item = QListWidgetItem(
                chat["title"]
            )

            item.setData(
                Qt.ItemDataRole.UserRole,
                chat["path"],
            )

            self.saved_list.addItem(
                item
            )

        layout.addWidget(
            self.saved_list,
            1,
        )

        button_layout = QHBoxLayout()

        load_button = QPushButton(
            "Load"
        )

        delete_button = QPushButton(
            "Delete"
        )

        close_button = QPushButton(
            "Close"
        )

        load_button.clicked.connect(
            self.load_selected_chat
        )

        delete_button.clicked.connect(
            self.delete_selected_chat
        )

        close_button.clicked.connect(
            self.saved_window.close
        )

        button_layout.addWidget(
            load_button
        )

        button_layout.addWidget(
            delete_button
        )

        button_layout.addWidget(
            close_button
        )

        layout.addLayout(
            button_layout
        )

        self.saved_window.show()

    # -------------------------
    # LOAD SAVED CHAT
    # -------------------------

    def load_selected_chat(self):
        item = (
            self.saved_list.currentItem()
        )

        if item is None:
            return

        path = item.data(
            Qt.ItemDataRole.UserRole
        )

        try:
            data = load_chat(path)

        except Exception as e:
            print(
                f"Could not load chat: {e}"
            )
            return

        self.conversation = data.get(
            "messages",
            [],
        )

        self.current_chat_title = (
            data.get(
                "title",
                "Saved Chat",
            )
        )

        self.clear_attachment()
        self.clear_chat_ui()

        for message in self.conversation:
            role = message.get(
                "role"
            )

            content = message.get(
                "content",
                "",
            )

            if role == "user":
                images = message.get(
                    "images",
                    [],
                )

                if images:
                    filename = os.path.basename(
                        images[0]
                    )

                    display_text = (
                        f"📎 {filename}\n\n"
                        f"{content}"
                    )

                else:
                    display_text = content

                bubble = MessageBubble(
                    "You",
                    display_text,
                    True,
                )

            elif role == "assistant":
                bubble = MessageBubble(
                    "PravithAI",
                    content,
                    False,
                )

            else:
                continue

            self.add_message(
                bubble
            )

        self.saved_window.close()

        self.scroll_to_bottom()
        self.input.setFocus()

    # -------------------------
    # DELETE SAVED CHAT
    # -------------------------

    def delete_selected_chat(self):
        item = (
            self.saved_list.currentItem()
        )

        if item is None:
            return

        path = item.data(
            Qt.ItemDataRole.UserRole
        )

        try:
            delete_chat(path)

        except Exception as e:
            print(
                f"Could not delete chat: {e}"
            )
            return

        self.saved_window.close()

        self.show_saved_chats()