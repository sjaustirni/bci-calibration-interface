from brainflow.board_shim import BoardShim, BrainFlowInputParams, BoardIds, BrainFlowPresets


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
            value = float(self.data.pop(0).split(" ")[1]) * 100
            return None, [value], [value]
        return self.board.get_board_data()
    
    def get_user_input(self, data=None):
        if data is None:
            data = self._get_data()
        
        emg_1 = data[1]
        emg_2 = data[2]
        
        if len(emg_1) > 0 or len(emg_2) > 0:
            return emg_1[0], emg_2[0]
        else:
            return 0, 0