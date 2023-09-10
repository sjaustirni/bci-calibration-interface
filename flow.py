from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds


class Flow:
    def __init__(self, playback=False):
        self.board = None
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
            self.board.start_stream()
    
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
