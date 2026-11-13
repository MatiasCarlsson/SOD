#!/usr/bin/env python3
"""
Generación automatizada de gráficos estadísticos en alta resolución (DPI 300)
para el Informe Final bajo normas APA (7.ª edición).
"""
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns

# Configuración de estilo visual acorde a estándares académicos APA
sns.set_theme(style="whitegrid", font="sans-serif")
plt.rcParams.update({
    "font.size": 11,
    "axes.labelsize": 12,
    "axes.titlesize": 13,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "legend.fontsize": 10,
    "figure.titlesize": 14,
    "figure.dpi": 300,
})

METRICS_DIR = "data/metrics"
FIGURES_DIR = "analysis/figures"
os.makedirs(FIGURES_DIR, exist_ok=True)


def plot_experiment_1():
    csv_file = os.path.join(METRICS_DIR, "experiment_1_volume.csv")
    if not os.path.exists(csv_file):
        print(f"Aviso: {csv_file} no encontrado. Omitiendo gráfico E1.")
        return

    df = pd.read_csv(csv_file)
    # Agrupar por dataset y engine calculando media y desvío
    agg = df.groupby(["dataset", "engine"])["execution_time_sec"].agg(["mean", "std"]).reset_index()

    plt.figure(figsize=(8, 5))
    palette = {"Python_Baseline": "#2b5c8f", "Hadoop_Streaming": "#d95f02", "Apache_Spark": "#2ca02c"}

    ax = sns.barplot(
        data=df,
        x="dataset",
        y="execution_time_sec",
        hue="engine",
        palette=palette,
        errorbar="sd",
        capsize=0.1,
    )

    plt.title("Figura 1\nComparación de Tiempo de Ejecución por Motor y Volumen de Datos (E1)", loc="left", fontweight="bold")
    plt.xlabel("Volumen de Dataset Sintético")
    plt.ylabel("Tiempo de Ejecución (segundos)")
    plt.legend(title="Motor de Procesamiento")
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "figura_1_comparacion_volumen.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Gráfico guardado: {out_path}")


def plot_experiment_2():
    csv_file = os.path.join(METRICS_DIR, "experiment_2_spark_scalability.csv")
    if not os.path.exists(csv_file):
        print(f"Aviso: {csv_file} no encontrado. Omitiendo gráfico E2.")
        return

    df = pd.read_csv(csv_file)
    agg = df.groupby("workers")["compute_time_sec"].mean().reset_index()

    t1 = agg.loc[agg["workers"] == 1, "compute_time_sec"].values[0]
    agg["speedup"] = t1 / agg["compute_time_sec"]
    agg["ideal_speedup"] = agg["workers"]

    fig, ax1 = plt.subplots(figsize=(8, 5))

    color = "#1f77b4"
    ax1.set_xlabel("Cantidad de Workers / Núcleos Asignados (p)")
    ax1.set_ylabel("Tiempo de Cómputo (s)", color=color)
    line1 = ax1.plot(agg["workers"], agg["compute_time_sec"], marker="o", color=color, linewidth=2, label="Tiempo Real")
    ax1.tick_params(axis="y", labelcolor=color)

    ax2 = ax1.twinx()
    color2 = "#2ca02c"
    ax2.set_ylabel("Factor de Aceleración (Speedup $S_p$)", color=color2)
    line2 = ax2.plot(agg["workers"], agg["speedup"], marker="s", color=color2, linewidth=2, label="Speedup Real")
    line3 = ax2.plot(agg["workers"], agg["ideal_speedup"], linestyle="--", color="gray", label="Speedup Ideal Lineal")
    ax2.tick_params(axis="y", labelcolor=color2)

    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc="center right")

    plt.title("Figura 2\nEscalabilidad y Aceleración de Apache Spark (E2)", loc="left", fontweight="bold")
    plt.xticks([1, 2, 3])
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "figura_2_speedup_spark.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Gráfico guardado: {out_path}")


def plot_experiment_5():
    csv_file = os.path.join(METRICS_DIR, "experiment_5_latency_summary.csv")
    if not os.path.exists(csv_file):
        print(f"Aviso: {csv_file} no encontrado. Omitiendo gráfico E5.")
        return

    df = pd.read_csv(csv_file)

    plt.figure(figsize=(8, 5))
    plt.errorbar(
        df["sensor_count"],
        df["mean_latency_ms"],
        yerr=df["std_latency_ms"],
        fmt="-o",
        color="#d62728",
        ecolor="#7f7f7f",
        elinewidth=2,
        capsize=5,
        label="Latencia Media ± $\\sigma$",
    )
    plt.plot(df["sensor_count"], df["p95_latency_ms"], "--^", color="#ff7f0e", label="Percentil 95 (P95)")

    plt.title("Figura 3\nLatencia de Respuesta del Controlador en Lazo Cerrado según Sensores Activos (E5)", loc="left", fontweight="bold")
    plt.xlabel("Cantidad de Sensores Simulados Concurrentes")
    plt.ylabel("Latencia Fin-a-Fin (milisegundos)")
    plt.legend()
    plt.tight_layout()

    out_path = os.path.join(FIGURES_DIR, "figura_3_latencia_controlador.png")
    plt.savefig(out_path)
    plt.close()
    print(f"Gráfico guardado: {out_path}")


def main():
    plot_experiment_1()
    plot_experiment_2()
    plot_experiment_5()


if __name__ == "__main__":
    main()

