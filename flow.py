from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds
from datetime import datetime
import os

class Flow:
    def __init__(self, playback=False):
        self.board = None
        # Get formatted UTC time
        self.now = datetime.utcnow()
        
        
        BoardShim.enable_dev_board_logger()
        self.playback = playback
        
        if self.playback:
            self.file = "emg-example.txt"
            self.data = None
        else:
            self.params = BrainFlowInputParams()
            self.params.ip_port = 6677
            self.params.ip_port_aux = 6678
            self.params.ip_address = "225.1.1.1"
            self.params.ip_address_aux = "225.1.1.1"
            self.params.master_board = BoardIds.SYNTHETIC_BOARD
    
    def start(self):
        if self.playback:
            with open(self.file, "r") as f:
                self.data = f.readlines()
        else:
            self.board = BoardShim(BoardIds.STREAMING_BOARD, self.params)
            self.board.prepare_session()
            os.makedirs("logs", exist_ok=True)
            self.board.start_stream(250*2, f"file://./logs/{self.now.strftime('%Y-%m-%d-%H-%M-%S')}.csv:w")
            
    def get_sample_rate(self):
        if self.playback:
            return 4000
        return self.board.get_sampling_rate(BoardIds.SYNTHETIC_BOARD)
    
    def stop(self):
        if not self.playback:
            self.board.stop_stream()
            self.board.release_session()
    
    def _get_data(self):
        if self.playback:
            try:
                value = float(self.data.pop(0).split(" ")[1]) * 100
                return None, [value]
            except IndexError:
                return None, []
        return self.board.get_board_data()
    
    def get_user_input(self, data=None):
        if data is None:
            data = self._get_data()
        
        emg = data[1]
        
        if len(emg) > 0:
            return emg[0]
        else:
            return None
