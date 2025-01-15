from abc import ABC


class Model(ABC):
    def __init__(self, model_name):
        self.model = None
        self.model_name = model_name

    def size(self):
        param_size = 0
        for param in self.model.parameters():
            param_size += param.nelement() * param.element_size()
        buffer_size = 0
        for buffer in self.model.buffers():
            buffer_size += buffer.nelement() * buffer.element_size()

        size_all_mb = (param_size + buffer_size) / 1024**2
        print('model size: {:.3f}MB'.format(size_all_mb))

    def summary(self):
        total_params = sum(p.numel() for p in self.model.parameters())
        trainable_params = sum(p.numel() for p in self.model.parameters() if p.requires_grad)
        return f"Model Summary:\n- Total Parameters: {total_params:,}\n- Trainable Parameters: {trainable_params:,}"

    def model_name(self):
        return self.model_name

    def get_model(self):
        return self.model

    def set_model(self, model):
        self.model = model

    def quantize_model(self):
        self.model.half()
