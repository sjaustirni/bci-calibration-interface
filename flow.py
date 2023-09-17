import os
from datetime import datetime

from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds


class Flow:
    def __init__(self, mode, channel=0, input_="cyton"):
        self.input = input_
        self.board = None
        # Get formatted UTC time
        self.now = datetime.utcnow()
        self.mode = mode
        self.channel = channel

        BoardShim.enable_dev_board_logger()

        self.board_id = BoardIds.STREAMING_BOARD if self._openbci() else BoardIds.CYTON_BOARD if self._cyton() else BoardIds.PLAYBACK_FILE_BOARD

        # https://brainflow-openbci.readthedocs.io/en/stable/SupportedBoards.html
        self.params = BrainFlowInputParams()
        if self._playback():
            self.params.master_board = BoardIds.CYTON_BOARD
            self.params.file = "emg-example.csv"

        if self._openbci():
            self.params.ip_port = 6677
            self.params.ip_port_aux = 6678
            self.params.ip_address = "225.1.1.1"
            self.params.ip_address_aux = "225.1.1.1"
            self.params.master_board = BoardIds.CYTON_BOARD
        elif self._cyton():
            self.params.serial_port = "COM4"

    def _openbci(self):
        return self.input == "openbci"

    def _cyton(self):
        return self.input == "cyton"

    def _playback(self):
        return self.input == "playback"

    def set_synthetic(self):
        self.params.master_board = BoardIds.SYNTHETIC_BOARD

    def start(self):
        os.makedirs("logs", exist_ok=True)
        self.board = BoardShim(self.board_id, self.params)
        self.board.prepare_session()
        self.board.start_stream(250 * 2, f"file://./logs/{self.now.strftime('%Y-%m-%d-%H-%M-%S')}_{self.mode}.csv:w")

    def get_sample_rate(self):
        if self._cyton():
            return self.board.get_sampling_rate(self.board_id)
        return self.board.get_sampling_rate(self.params.master_board)

    def stop(self):
        self.board.stop_stream()
        self.board.release_session()

    def _get_data(self):
        return self.board.get_board_data()

    def get_user_input(self, data=None):
        if data is None:
            data = self._get_data()

        emg = data[self.channel]

        if len(emg) > 0:
            return emg
        else:
            return None
