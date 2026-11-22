"""Single experimenter window followed by full-screen stimulus presentation."""
import json
import secrets
import sys
import traceback
from pathlib import Path

from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QComboBox, QPushButton, QFileDialog, QMessageBox, QCheckBox)
from .stimuli import discover, make_main_trials, make_practice_trials, seed_from_session_label, order_quality_report
from .storage import create_session, safe_id
from .sdt import analyze_csv


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Joint Perception Lab — prototype v0.6')
        self.resize(650, 420)
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.addWidget(QLabel('JOINT PERCEPTION LAB  |  Experimenter setup'))
        self.task = QComboBox()
        self.task.addItems(['Biological motion detection', 'Line bisection'])
        layout.addWidget(QLabel('Task'))
        layout.addWidget(self.task)
        self.condition = QComboBox()
        self.condition.addItems(['Individual', 'Shared — Host', 'Shared — Client'])
        layout.addWidget(QLabel('Condition'))
        layout.addWidget(self.condition)
        layout.addWidget(QLabel('Host IP address (client only; default 192.168.1.211)'))
        self.host_ip = QLineEdit('192.168.1.211')
        layout.addWidget(self.host_ip)
        layout.addWidget(QLabel('Shared session label (must match on both computers)'))
        self.session_label = QLineEdit('session01')
        layout.addWidget(self.session_label)
        layout.addWidget(QLabel('IMPORTANT: Start HOST first and wait; only then start CLIENT. Use a NEW shared label for each dyad.'))
        layout.addWidget(QLabel('Participant ID'))
        self.participant = QLineEdit('test001')
        layout.addWidget(self.participant)
        layout.addWidget(QLabel('Video stimulus folder (MP4 recommended)'))
        row = QHBoxLayout()
        self.folder = QLineEdit(str(Path.cwd()/'stimuli'/'biological_motion'))
        row.addWidget(self.folder)
        browse = QPushButton('Browse…')
        browse.clicked.connect(self.browse)
        row.addWidget(browse)
        layout.addLayout(row)
        self.fullscreen = QCheckBox('Full-screen experiment')
        self.fullscreen.setChecked(True)
        layout.addWidget(self.fullscreen)
        self.check_button = QPushButton('Validate stimuli')
        self.check_button.clicked.connect(self.validate)
        layout.addWidget(self.check_button)
        self.start_button = QPushButton('Start experiment')
        self.start_button.clicked.connect(self.start)
        layout.addWidget(self.start_button)
        self.status = QLabel('v0.6: Start HOST first, wait for connection, THEN start CLIENT. Biological motion: two balanced blocks; bisection: 146 trials. Shared timing unvalidated.')
        self.status.setWordWrap(True)
        layout.addWidget(self.status)
        self.setCentralWidget(root)

    def browse(self):
        path = QFileDialog.getExistingDirectory(self, 'Choose stimulus folder', self.folder.text())
        if path:
            self.folder.setText(path)

    def get_trials(self, seed=None):
        if self.task.currentIndex() != 0:
            from .bisection import make_order, PRACTICE_POSITIONS
            return make_order(seed if seed is not None else 20260607), [{'trial':i+1,'target_position':p} for i,p in enumerate(PRACTICE_POSITIONS)]
        stimuli = discover(self.folder.text())
        main = make_main_trials(stimuli, seed=seed if seed is not None else 20260607)
        practice = make_practice_trials(stimuli)
        return main, practice

    def validate(self):
        try:
            main, practice = self.get_trials()
            self.status.setText(f'Validated: {len(main)} main trials, {len(practice)} practice trials.' + (' No external files required.' if self.task.currentIndex() else ''))
        except Exception as exc:
            QMessageBox.warning(self, 'Validation failed', str(exc))

    def start(self):
        try:
            participant = safe_id(self.participant.text())
            role = ('individual', 'host', 'client')[self.condition.currentIndex()]
            from .bisection import shared_seed, write_order as write_bisection_order, PRACTICE_POSITIONS
            bisection = self.task.currentIndex() == 1
            seed = (20260427 if bisection else
                    (secrets.randbits(64) if role == 'individual'
                     else seed_from_session_label(self.session_label.text())))
            main, practice = self.get_trials(seed=seed)
            # Fail before creating a session if dependencies are missing.
            if not bisection:
                import cv2  # noqa: F401
            import psychopy  # noqa: F401
            config = {'task':'line_bisection' if bisection else 'biological_motion', 'condition':'shared' if role != 'individual' else 'individual',
                      'network_role':role, 'session_label':self.session_label.text(),
                      'stimulus_folder':str(Path(self.folder.text()).resolve()),
                      'fullscreen':self.fullscreen.isChecked(),
                      'main_seed':seed, 'practice_seed':20260608,
                      'fixation_s':.5, 'feedback_s':.8,
                      'timing_status':'SOFTWARE QC — hardware timing unvalidated', 'software_version':'0.6',
                      'sequence_method':('73 positions -900 to 900 step 25, each twice; fixed seeded shuffle (20260427)' if bisection else 'two 80-trial blocks; cyclic binary transitions 20 per pair per block'),
                      'order_quality':({ 'positions':73, 'repetitions':2 } if bisection else order_quality_report(main))}
            if bisection:
                from datetime import datetime, timezone
                import json
                stamp = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')
                session_id = f'{participant}_{config["condition"]}_{stamp}'
                folder = Path.cwd()/'data'/session_id
                folder.mkdir(parents=True, exist_ok=False)
                (folder/'session.json').write_text(json.dumps({'session_id':session_id, 'participant_id':participant, 'config':config},indent=2),encoding='utf-8')
                write_bisection_order(folder, main, PRACTICE_POSITIONS)
            else:
                folder, session_id = create_session(Path.cwd()/'data', participant,
                                                     config['condition'], config, main, practice)
        except Exception as exc:
            QMessageBox.critical(self, 'Cannot start', str(exc))
            return
        self.hide()
        QApplication.processEvents()
        error = None
        try:
            if bisection:
                from .bisection import run_line_bisection
                run_line_bisection(participant, session_id, folder, main,
                                   fullscreen=self.fullscreen.isChecked(),role=role,
                                   peer_address=self.host_ip.text().strip(),
                                   session_label=self.session_label.text().strip())
            else:
                from .experiment import run_biological_motion
                run_biological_motion(participant, session_id, folder, main, practice,
                                      fullscreen=self.fullscreen.isChecked(), role=role,
                                      peer_address=self.host_ip.text().strip(),
                                      session_label=self.session_label.text().strip())
        except KeyboardInterrupt as exc:
            error = f'Experiment interrupted: {exc}'
        except Exception:
            error = traceback.format_exc()
        finally:
            self.show()
            self.raise_()
            self.activateWindow()
        if error:
            (folder/'error.log').write_text(error, encoding='utf-8')
            QMessageBox.warning(self, 'Session ended with error',
                                f'{error[-1800:]}\n\nPartial data, if any, are saved in:\n{folder}')
        else:
            if bisection:
                QMessageBox.information(self,'Completed',f'Bisection data saved to:\n{folder}\n\nFile: bisection_trials.csv')
                return
            try:
                summary = analyze_csv(folder/'trials.csv')
                QMessageBox.information(self, 'Completed',
                    f'Session saved to:\n{folder}\n\nTiming QC: timing_report.json\n\nSDT summary:\n{summary}')
            except Exception as exc:
                QMessageBox.warning(self, 'Completed; analysis unavailable',
                    f'Session saved to {folder}\nSDT summary error: {exc}')


def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    return app.exec()
