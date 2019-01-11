import numpy as np
import torch
import torch.nn as nn
import torch.utils.data as Data
global test_data, test_label, cnn
# 数据处理完成，卷积训练


# Hyper Parameters
EPOCH = 50  # train the training data n times, to save time, we just train 1 epoch
BATCH_SIZE = 60
LR = 0.001  # learning rate
save_model = False


def load_test_data(filename):
    test_data, test_label = quickload(filename)
    test_data = test_data[:, np.newaxis]

    test_data = torch.tensor(test_data)
    test_label = torch.tensor(test_label)
    return test_data, test_label


class CNN(nn.Module):
    def __init__(self):
        super(CNN, self).__init__()

        self.conv1 = nn.Sequential(  # input shape (1, 120, 160)
            nn.Conv2d(
                in_channels=1,  # input height
                out_channels=16,  # n_filters
                kernel_size=5,  # filter size
                stride=1,  # filter movement/step
                padding=2,
                # if want same width and length of this image after Conv2d, padding=(kernel_size-1)/2 if stride=1
            ),  # output shape (16, 28, 28)
            nn.BatchNorm2d(16),
            nn.ReLU(inplace=True),  # activation
            nn.MaxPool2d(kernel_size=2),  # choose max value in 2x2 area, output shape (16, 14, 14)
        )
        self.conv2 = nn.Sequential(  # input shape (16, 60, 80)
            nn.Conv2d(16, 32, 5, 1, 2),  # output shape (32, 60, 80)
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),  # activation
            nn.MaxPool2d(2),  # output shape (32, 30, 40)
        )
        self.conv3 = nn.Sequential(  # input shape (32, 30, 40)
            nn.Conv2d(32, 64, 5, 1, 2),  # output shape (64, 30, 40)
            nn.BatchNorm2d(64),
            nn.ReLU(inplace=True),  # activation
            nn.MaxPool2d(2),  # output shape (64, 15, 20)
        )
        self.conv4 = nn.Sequential(  # input shape (64, 15, 20)
            nn.Conv2d(64, 128, 5, 1, 2),  # output shape (128, 15, 20)
            nn.BatchNorm2d(128),
            nn.ReLU(inplace=True),  # activation
        )
        self.conv5 = nn.Sequential(  # input shape (128, 15, 20)
            nn.Conv2d(128, 256, 5, 1, 2),  # output shape (128, 15, 20)
            nn.BatchNorm2d(256),
            nn.Dropout(0.8),
            nn.ReLU(inplace=True),  # activation
        )
        self.conv6 = nn.Sequential(  # input shape (128, 15, 20)
            nn.Conv2d(256, 512, 5, 1, 2),  # output shape (128, 15, 20)
            nn.BatchNorm2d(512),
            nn.Dropout(0.7),
            nn.ReLU(inplace=True),  # activation
        )
        self.conv7 = nn.Sequential(  # input shape (128, 15, 20)
            nn.Conv2d(512, 1024, 5, 1, 2),  # output shape (128, 15, 20)
            nn.BatchNorm2d(1024),
            nn.ReLU(inplace=True),  # activation
        )
        self.out = nn.Sequential(
            nn.Linear(1024 * 15 * 20, 1024),
            nn.Dropout(0.7),
            nn.Linear(1024, 3),  # fully connected layer, output 7 classes
        )

    def forward(self, x):
        x = self.conv1(x.float())
        x = self.conv2(x.float())
        x = self.conv3(x.float())
        x = self.conv4(x.float())
        x = self.conv5(x.float())
        x = self.conv6(x.float())
        x = self.conv7(x.float())
        # for i in range(3):
        #     x=self.conv(x.float())
        x = x.view(x.size(0), -1)  # flatten the output of conv2 to (batch_size, 32 * 7 * 7)
        output = self.out(x)
        return output, x  # return x for visualization


def restore_params(model):
    print("restore parameters")
    # model.conv1.load_state_dict(torch.load('./conv1.pkl'))
    # model.conv2.load_state_dict(torch.load('./conv2.pkl'))
    # model.conv3.load_state_dict(torch.load('./conv3.pkl'))
    # model.conv4.load_state_dict(torch.load('./conv4.pkl'))
    # model.conv5.load_state_dict(torch.load('./conv5.pkl'))
    # model.conv6.load_state_dict(torch.load('./conv6.pkl'))
    # model.out.load_state_dict(torch.load('./out.pkl'))
    model.conv1.load_state_dict(torch.load('../sort/conv1.pkl'))
    model.conv2.load_state_dict(torch.load('../sort/conv2.pkl'))
    model.conv3.load_state_dict(torch.load('../sort/conv3.pkl'))
    model.conv4.load_state_dict(torch.load('../sort/conv4.pkl'))
    model.conv5.load_state_dict(torch.load('../sort/conv5.pkl'))
    model.conv6.load_state_dict(torch.load('../sort/conv6.pkl'))
    model.conv7.load_state_dict(torch.load('../sort/conv7.pkl'))
    model.out.load_state_dict(torch.load('../sort/out.pkl'))


def test(model, test_loader):
    acc = np.array(0)
    for step, (b_x, b_y) in enumerate(test_loader):  # gives batch data, normalize x when iterate train_loader
        b_x = b_x.cuda()
        test_output, _ = model(b_x)
        test_output = test_output.cuda()
        pred_y = torch.max(test_output, 1)[1].cpu().data.numpy()
        acc += np.sum((pred_y == b_y.data.numpy()).astype(int))
    accuracy = float(acc) / float((step + 1) * test_loader.batch_size)
    return accuracy


def loadimg(path):
    print("load img:", path)
    import cv2
    img = cv2.imread(path, 0)
    for i in range(2):
        img = cv2.pyrDown(img)
    img = ((img.reshape(-1) - 128) / 128).reshape(img.shape)[np.newaxis, np.newaxis]
    return img


def test_sample(model, data, label):
    # data=data
    test_output, _ = model(data)
    test_output = test_output.cuda()
    pred_y = torch.max(test_output, 1)[1].cpu().data.numpy()[0]
    print("predict: ", pred_y)
    # print("real   : ", int(label))
    return str(pred_y)


def quickload(filename):
    print("quick load method")
    data = np.load(filename)
    # normalization
    data = ((data.reshape(-1) - 128) / 128).reshape(data.shape)
    rawData = []
    (_, n, l, w) = data.shape
    for i in range(3):
        # 给数据加上标注信息
        label = (np.ones(n) * (i))[:, np.newaxis]
        # 图片矩阵拉平
        rawData.append(np.concatenate((data[i].reshape(n, -1), label), axis=1))
    # 合并3类数据并shuffle
    datus = np.array(rawData).reshape(3 * n, -1)
    # np.random.shuffle(datus)
    data = datus[:, :-1]
    label = datus[:, -1]
    data = data.reshape(-1, l, w)
    return data, label




def init_dataloader(data, label, batch_size):
    torch_dataset = Data.TensorDataset(data, label)
    # 把 dataset 放入 DataLoader
    loader = Data.DataLoader(
        dataset=torch_dataset,  # torch TensorDataset format
        batch_size=batch_size,  # mini batch size
        shuffle=False,  # 要不要打乱数据 (打乱比较好)
        # shuffle=True,  # 要不要打乱数据 (打乱比较好)
        num_workers=1,  # 多线程来读数据
    )
    return loader




def initNet():
    global test_data, test_label, cnn
    TEST_BATCH_SIZE = 1
    print("model define")
    cnn = CNN()
    cnn.cuda()
    # 恢复参数
    restore_params(cnn)
    cnn.eval()
    ### test alg_______________________
    # test_data, test_label = load_test_data("./test.npy")
    # test_loader = init_dataloader(test_data, test_label, TEST_BATCH_SIZE)
    # accuracy = test(cnn, test_loader)
    # print("test accuracy:", accuracy)
    ###_______________________________
    test_data, test_label = load_test_data("../sort/test.npy")


def guitest(filename):
    global test_data, test_label, cnn
    sample_data = test_data[0].cpu().numpy()[np.newaxis]
    # sample_label = test_label[index].cpu().numpy()[np.newaxis]
    # sample_data = torch.tensor(sample_data).cuda()
    # pred = test_sample(cnn, sample_data, sample_label)
    ###read img
    # print("sample_data1:",sample_data)
    sample_data = torch.tensor(loadimg(filename)).cuda()

    # print("sample_data2:",sample_data)
    sample_label = np.array(0)
    pred = test_sample(cnn, sample_data, sample_label)
    return pred



def main():
    cnn=initNet()
    for i in range(300, 310):
        guitest(i,cnn)


if __name__ == '__main__':
    # main()
    initNet()
