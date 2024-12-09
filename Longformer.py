from huggingface_hub import login
login() #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
import os ### pip install pyarrow multiprocess aiohttp xxhash accelerate
### pip install huggingface_hub torch transformers pandas
os.environ["CUDA_VISIBLE_DEVICES"] = "0,1"
os.environ["PYTORCH_CUDA_ALLOC_CONF"] = "max_split_size_mb:128"
import torch ### source /etc/network_turbo
from transformers import LongformerForSequenceClassification, LongformerTokenizer, Trainer, TrainingArguments,AutoTokenizer
from datasets import load_dataset, load_metric ### pip install --no-deps datasets==1.18.3
from sklearn.model_selection import train_test_split
import pandas as pd
# Load model directly
from transformers import AutoModel
import numpy as np
df = pd.read_json('output.json', lines=True)
df1 = df[df['content'] != '']

# 假设你有一个包含文本和标签的列表
# texts = ["这是一个正面文本", "这是一个负面文本", ...]  # 你的文本数据
# labels = [1, 0, ...]  # 对应的标签（1表示正面，0表示负面）
texts = df1.content.tolist()
labels = df1.url.tolist()

# 假设你有一个包含文本和标签的CSV文件
# 数据格式示例：文本,标签
# 例如：I love this product,1
#       This service is terrible,0
# data = pd.read_csv('your_binary_classification_data.csv')
 
# 将数据分为训练集和测试集（这里为了简化，我们不再单独划分验证集）
train_texts, test_texts, train_labels, test_labels = train_test_split(texts, labels, test_size=0.2, random_state=42)
 
# 初始化Longformer的分词器
# model = AutoModel.from_pretrained("allenai/longformer-base-4096")
# tokenizer = LongformerTokenizer.from_pretrained('longformer-base-4096')
tokenizer = AutoTokenizer.from_pretrained("allenai/longformer-base-4096")

# 数据预处理函数
def preprocess_function(examples):
    # 对文本进行分词
    encodings = tokenizer(examples['text'], truncation=True, padding='max_length', max_length=4096)
    # 将标签转换为tensor
    encodings['labels'] = torch.tensor(examples['label'])
    return encodings
 
# 创建数据集对象（这里为了简化，我们直接使用字典来模拟数据集）
train_dataset = {'text': train_texts, 'label': train_labels}
test_dataset = {'text': test_texts, 'label': test_labels}
 
# 应用预处理函数
train_encodings = preprocess_function(train_dataset)
test_encodings = preprocess_function(test_dataset)
 
# 将数据集转换为PyTorch的Dataset对象（这里为了简化，我们直接使用字典）
# 在实际应用中，你可能需要创建一个自定义的Dataset类
class CustomDataset(torch.utils.data.Dataset):
    def __init__(self, encodings):
        self.encodings = encodings
 
    def __getitem__(self, idx):
        item = {key: torch.tensor(val[idx]) for key, val in self.encodings.items()}
        return item
 
    def __len__(self):
        return len(self.encodings['input_ids'])
 
train_dataset = CustomDataset(train_encodings)
test_dataset = CustomDataset(test_encodings)
 
# 设置训练参数
training_args = TrainingArguments(
    output_dir='./results',
    num_train_epochs=1,
    per_device_train_batch_size=8,
    per_device_eval_batch_size=8,
    warmup_steps=500,
    weight_decay=0.01,
    logging_dir='./logs',
    logging_steps=10,
    evaluation_strategy="epoch"
)
 
# 加载Longformer模型并设置为二分类任务
# model = LongformerForSequenceClassification.from_pretrained('longformer-base-4096', num_labels=2)
model = LongformerForSequenceClassification.from_pretrained("allenai/longformer-base-4096", num_labels=2)
# model = AutoModel.from_pretrained("allenai/longformer-base-4096",num_labels = 2)
 
# 定义计算评估指标的函数
metric = load_metric("accuracy")
 
def compute_metrics(p):
    if isinstance(p.predictions, np.ndarray):
        predictions_tensor = torch.tensor(p.predictions)
    else:
        predictions_tensor = p.predictions
 
    preds = torch.argmax(predictions_tensor, axis=1)
    return metric.compute(predictions=preds, references=p.label_ids)
 
# 实例化Trainer
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=test_dataset,
    compute_metrics=compute_metrics,
)
 
# 开始训练
trainer.train()
 
# 评估模型
eval_result = trainer.evaluate()
print(f"Evaluation results: {eval_result}")
 
# 保存模型
model.save_pretrained('./longformer-binary-classification')
tokenizer.save_pretrained('./longformer-binary-classification')