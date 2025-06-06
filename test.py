import torch
print(torch.cuda.is_available())  # Should return True
print(torch.cuda.device_count())  # Should show your GPU
print(torch.version.cuda)  # Should show your GPU
# print(torchvision.ops.nms(boxes.cpu(), scores.cpu(), iou_threshold))  # Test CPU version