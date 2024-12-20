import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import roc_auc_score, precision_score, recall_score, accuracy_score, roc_curve
from sklearn.neural_network import MLPClassifier
from sklearn.preprocessing import StandardScaler
from imblearn.over_sampling import SMOTE

# Загрузка данных
data = pd.read_csv('/content/sample_data/german .csv', sep=';')
X = data.iloc[:, 1:].to_numpy()
y = data.iloc[:, 0].to_numpy()

# Разделение данных на обучающую и тестовую выборки
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Обработка несбалансированных данных с помощью SMOTE
smote = SMOTE(random_state=42)
X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)

# Нормализация данных
scaler = StandardScaler()
X_train_resampled = scaler.fit_transform(X_train_resampled)
X_test_scaled = scaler.transform(X_test)

# Обучение Random Forest для сравнения
rf_model = RandomForestClassifier(n_estimators=100, random_state=42)
rf_model.fit(X_train_resampled, y_train_resampled)

# Прогноз на тестовых данных для Random Forest
rf_pred_proba = rf_model.predict_proba(X_test_scaled)[:, 1]

# Расчет метрик для Random Forest
rf_roc_auc = roc_auc_score(y_test, rf_pred_proba)
print("Random Forest ROC AUC:", rf_roc_auc)

# Обучение MLP с улучшенной архитектурой и гиперпараметрами
mlp_model = MLPClassifier(hidden_layer_sizes=(100, 50),  # Увеличено количество нейронов
                          activation='relu',  # Можно попробовать 'tanh'
                          solver='adam',  # Используем Adam
                          max_iter=2000,  # Увеличено количество эпох
                          alpha=0.001,  # Регуляризация
                          random_state=42,
                          early_stopping=True,  # Остановимся при переобучении
                          validation_fraction=0.1,  # Доля для валидации
                          n_iter_no_change=50)  # Количество итераций без улучшения

mlp_model.fit(X_train_resampled, y_train_resampled)

# Прогноз на тестовых данных для MLP
mlp_pred_proba = mlp_model.predict_proba(X_test_scaled)[:, 1]

# Расчет метрик для MLP нейронной сети
mlp_roc_auc = roc_auc_score(y_test, mlp_pred_proba)
mlp_accuracy = accuracy_score(y_test, (mlp_pred_proba > 0.5).astype(int))
mlp_precision = precision_score(y_test, (mlp_pred_proba > 0.5).astype(int))
mlp_recall = recall_score(y_test, (mlp_pred_proba > 0.5).astype(int))

print("\nMLP (Neural Network) метрики:")
print(f"ROC AUC: {mlp_roc_auc:.2f}")
print(f"Accuracy: {mlp_accuracy:.2f}")
print(f"Precision: {mlp_precision:.2f}")
print(f"Recall: {mlp_recall:.2f}")

# Визуализация ROC-кривых
plt.figure(figsize=(10, 6))
fpr_rf, tpr_rf, _ = roc_curve(y_test, rf_pred_proba)
fpr_mlp, tpr_mlp, _ = roc_curve(y_test, mlp_pred_proba)

plt.plot(fpr_rf, tpr_rf, label='Random Forest (AUC = {:.2f})'.format(rf_roc_auc))
plt.plot(fpr_mlp, tpr_mlp, label='MLP (AUC = {:.2f})'.format(mlp_roc_auc))
plt.plot([0, 1], [0, 1], 'k--')
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC Curve')
plt.legend()
plt.show()