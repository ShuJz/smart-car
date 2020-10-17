import tvm
from tvm import relay
from tvm import autotvm

# PyTorch imports
import torch


######################################################################
# Load a pretrained PyTorch model
# -------------------------------
model_path = 'mobilenet-nnconv5dw-skipadd-pruned.pth.tar'
checkpoint = torch.load(model_path, map_location='cpu')
if type(checkpoint) is dict:
    best_result = checkpoint['best_result']
    model = checkpoint['model']
    print("=> loaded best model (epoch {})".format(checkpoint['epoch']))
else:
    model = checkpoint

model = model.eval()

# We grab the TorchScripted model via tracing
input_shape = [1, 3, 224, 224]
input_data = torch.randn(input_shape)
scripted_model = torch.jit.trace(model, input_data).eval()
# scripted_model = model

######################################################################
# Import the graph to Relay
# -------------------------
# Convert PyTorch graph to Relay graph. The input name can be arbitrary.
input_name = "0"
shape_list = [(input_name, input_shape)]
mod, params = relay.frontend.from_pytorch(scripted_model, shape_list)

######################################################################
# Relay Build
# -----------
# Compile the graph to llvm target with given input specification.
# target = "llvm"
target = 'llvm -device=arm_cpu -model=bcm2711 -mtriple=arm-linux-gnueabihf -mattr=+neon'
target_host = "llvm"
log_file = 'tvm_compile/tuning/rbp4b.fast_depth.log'
# ctx = tvm.context(target)
with autotvm.apply_history_best(log_file):
    with tvm.transform.PassContext(opt_level=3):
        graph, lib, params = relay.build(mod, target=target, params=params)

# Save the library at local temporary directory.

path = 'compiled/'
path_lib = path + "deploy_lib.tar"
path_graph = path + "deploy_graph.json"
path_params = path + "deploy_param.params"
lib.export_library(path_lib)
with open(path_graph, "w") as fo:
    fo.write(graph)
with open(path_params, "wb") as fo:
    fo.write(relay.save_param_dict(params))