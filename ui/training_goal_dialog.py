        self._btn_fast.clicked.connect(lambda: self._select_goal("fast"))
        options_layout.addWidget(self._btn_fast)

        # Max Accuracy
        self._btn_max = QPushButton("Maximum Accuracy")
        self._btn_max.setStyleSheet("""
            QPushButton {
                background: rgba(85, 255, 85, 0.15);
                border: 2px solid #55ff55;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(85, 255, 85, 0.25);
            }
        """)
        self._btn_max.clicked.connect(lambda: self._select_goal("max_accuracy"))
        options_layout.addWidget(self._btn_max)

        layout.addLayout(options_layout)

        # Descriptions
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(120)
        desc_text.setStyleSheet("""
            QTextEdit {
                background: #1a1a2e;
                color: #aaa;
                border: none;
                font-size: 8.5pt;
            }
        """)
        desc_text.setHtml("""
        <b>Balanced:</b> Good trade-off between training time and final accuracy. Recommended for most use cases.<br><br>
        <b>Fast:</b> Minimize training time. Skip SSL pre-training, reduce epochs. Good for prototyping.<br><br>
        <b>Maximum Accuracy:</b> Full SHADA pipeline with all optimizations. Longer training but best results.
        """)
        layout.addWidget(desc_text)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(35)
        layout.addWidget(cancel_btn)

    def _select_goal(self, goal: str):
        self._goal = goal
        self.accept()

    def get_goal(self) -> str:
        return self._goal