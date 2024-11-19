import streamlit as st
import plotly.express as px
import pandas as pd
import requests
from config import HOST

# Настройка заголовка приложения
st.title("Путешествие в мир ИИ")


# Создание вкладок
tab1, tab2 = st.tabs(["Анализ видео", "Лидерборд"])

with tab1:
    st.header("Анализ видео")
    if st.button("Обновить результаты", type="primary"):
        response = requests.get(f"{HOST}/get_teams_class_counts", verify=False).json()
        if response["status"] == "ok":
            team_class_counts = response["teams_class_counts"]
            for class_name in team_class_counts.keys():
                plot_data = team_class_counts[class_name]
                ground_truth = plot_data.pop("ground_truth")

                # Создаем вертикальный график с разными цветами для каждого столбца
                fig = px.bar(
                    x=list(plot_data.keys()),  # По оси X - названия классов
                    y=list(plot_data.values()),  # По оси Y - значения
                    title=f"Анализ класса {class_name}",
                    color=list(plot_data.keys()),  # Используем значения для задания цвета
                    color_discrete_sequence=px.colors.qualitative.Pastel  # Выбираем цветовую палитру
                )

                fig.add_shape(
                    type="line",
                    x0=-0.5,  # Начальная позиция по оси X
                    x1=len(plot_data) - 0.5,  # Конечная позиция по оси X
                    y0=ground_truth,  # Уровень Y для линии
                    y1=ground_truth,  # Уровень Y для линии
                    line=dict(color="red", width=5, dash="dash")  # Настройки линии
                )

                # Обновляем оси
                fig.update_layout(xaxis_title="Классы", yaxis_title="Количество")

                st.plotly_chart(fig)
        else: 
            st.error("Ошибка")


# Вторая вкладка: Ввод данных о зверях
with tab2:
    st.header("Лидерборд")
    if st.button("Обновить лидерборд", type="primary"):
        response = requests.get(f"{HOST}/get_teams_yolo_results", verify=False).json()
        if response["status"] == "ok":
            team_yolo_results = response["teams_yolo_results"]
            df = pd.DataFrame(team_yolo_results)
            df = df.drop(["id"], axis=1)
            lead = pd.DataFrame(columns=["team", "score", "params"])
            teams = df["name"].values
            for team in teams:
                best_score = df[df["name"] == team]["score"].max()
                best_params = df[(df["name"] == team) & (df["score"] == best_score)]["params"]
                lead.loc[len(lead)] = [team, best_score, best_params]
            lead = lead.sort_values(by="score", ascending=True)
            fig = px.bar(lead, x="team", y="score", hover_data="params")
            st.plotly_chart(fig)
            st.dataframe(lead)
            
        else: 
            st.error("Ошибка")