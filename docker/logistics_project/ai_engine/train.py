import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import MobileNetV2
from tensorflow.keras.layers import Dense, GlobalAveragePooling2D, Dropout
from tensorflow.keras.models import Model
from tensorflow.keras.optimizers import Adam
import os
import matplotlib.pyplot as plt

# 1. 配置参数
BATCH_SIZE = 8
IMG_SIZE = (224, 224)
DATASET_DIR = "dataset"
MODEL_SAVE_PATH = "model/my_custom_model.keras"
EPOCHS = 5

def train():
    if not os.path.exists(DATASET_DIR):
        print("Dataset not found! Please run 'python prepare_data.py' first.")
        return

    print("Loading data...")
    # 2. 数据增强与加载
    train_datagen = ImageDataGenerator(
        rescale=1./255,
        rotation_range=20,
        horizontal_flip=True,
        fill_mode='nearest'
    )

    val_datagen = ImageDataGenerator(rescale=1./255)

    train_generator = train_datagen.flow_from_directory(
        os.path.join(DATASET_DIR, 'train'),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical'
    )

    validation_generator = val_datagen.flow_from_directory(
        os.path.join(DATASET_DIR, 'validation'),
        target_size=IMG_SIZE,
        batch_size=BATCH_SIZE,
        class_mode='categorical',
        classes=list(train_generator.class_indices.keys()) # [FIX] 强制使用和训练集一致的类别列表
    )

    # 动态获取类别数量 (Roboflow 数据集可能有多个细分类别)
    num_classes = len(train_generator.class_indices)
    print(f"Detected {num_classes} classes: {train_generator.class_indices}")

    # 3. 构建模型 (迁移学习)
    print("Building model (MobileNetV2)...")
    base_model = MobileNetV2(weights='imagenet', include_top=False, input_shape=IMG_SIZE + (3,))
    
    # 冻结预训练层 (前几层)
    base_model.trainable = False 

    # 添加自定义头部
    x = base_model.output
    x = GlobalAveragePooling2D()(x)
    x = Dense(128, activation='relu')(x)
    x = Dropout(0.5)(x)
    predictions = Dense(num_classes, activation='softmax')(x) # 动态适配类别数

    model = Model(inputs=base_model.input, outputs=predictions)

    model.compile(optimizer=Adam(learning_rate=0.0001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    # 4. 训练
    print(f"Starting training for {EPOCHS} epochs...")
    history = model.fit(
        train_generator,
        epochs=EPOCHS,
        validation_data=validation_generator
    )

    # 5. 保存模型 (Keras 3 格式)
    print(f"Saving model to {MODEL_SAVE_PATH}...")
    model.save(MODEL_SAVE_PATH)
    
    # 保存 Label 映射
    import json
    labels_path = "model/labels.json"
    with open(labels_path, 'w') as f:
        json.dump(train_generator.class_indices, f)
    print(f"Class indices saved to {labels_path}")

    print("Training finished!")
    
    # 简单的图表 (如果有 matplotlib)
    try:
        acc = history.history['accuracy']
        val_acc = history.history['val_accuracy']
        plt.plot(acc, label='Training Accuracy')
        plt.plot(val_acc, label='Validation Accuracy')
        plt.legend()
        plt.title('Training Results')
        plt.savefig('training_plot.png')
        print("Plot saved to training_plot.png")
    except:
        pass

if __name__ == "__main__":
    train()
