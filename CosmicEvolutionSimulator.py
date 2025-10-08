import numpy as np
import random
import math
import sys
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer, Qt
from PyQt5.QtGui import QFont, QIcon
import pyqtgraph.opengl as gl
import json
import os
from datetime import datetime

cosmology_data = {
    "DARK_MATTER": ("DM", 1.0, 0, 1e30, 0, (0.2, 0.2, 0.6, 1)),
    "DARK_ENERGY": ("DE", 0.0, 0, 1e30, 0, (0.6, 0.2, 0.6, 1)),
    "HYDROGEN": ("H", 0.938, 1, 1e30, 0.5, (0.1, 0.5, 0.9, 1)),
    "HELIUM": ("He", 3.727, 2, 1e30, 0, (0.3, 0.7, 0.9, 1)),
    "NEUTRON": ("n", 0.940, 0, 880, 0.5, (0.7, 0.7, 0.7, 1)),
    "PHOTON": ("γ", 0, 0, 1e30, 1, (1, 1, 0.8, 1)),
    "NEUTRINO": ("ν", 1e-9, 0, 1e30, 0.5, (0.8, 0.8, 1, 1)),
    "ELECTRON": ("e-", 0.000511, -1, 1e30, 0.5, (1, 0.3, 0.3, 1)),
    "PROTON": ("p+", 0.938, 1, 1e30, 0.5, (1, 0.5, 0.5, 1)),
    "QUARK_UP": ("u", 0.003, 0.667, 1e30, 0.5, (0.9, 0.2, 0.2, 1)),
    "QUARK_DOWN": ("d", 0.006, -0.333, 1e30, 0.5, (0.2, 0.2, 0.9, 1)),
    "GRAVITON": ("G", 0, 0, 1e30, 2, (0.5, 0.8, 0.5, 1)),
    "STAR": ("★", 1000, 0, 1e20, 0, (1, 1, 0.3, 1)),
    "GALAXY": ("🌀", 10000, 0, 1e25, 0, (0.8, 0.4, 0.8, 1)),
    "BLACK_HOLE": ("●", 100000, 0, 1e30, 0, (0.1, 0.1, 0.1, 1))
}

def initialize_simulator_state():
    return {
        'particles': [],
        'interaction_events': [],
        'gravitational_pairs': [],
        'time': 0.0,
        'scale_factor': 1.0,
        'event_counter': 0,
        'particle_counter': 0,
        'interaction_distance': 0.5,
        'fusion_probability': 0.1,
        'structure_formation_probability': 0.05,
        'initial_energy': 3.0,
        'num_particles': 20,
        'universe_age': 13.8,
        'dark_matter_ratio': 0.27,
        'dark_energy_ratio': 0.68,
        'baryonic_ratio': 0.05,
        'expansion_rate': 0.00002,
        'gravitational_constant': 1e-15,
        'cosmic_inflation': False,
        'quantum_fluctuations': True,
        'max_position': 10.0
    }

simulator_state = initialize_simulator_state()

particles = []
interaction_events = []
gravitational_pairs = []
particle_items = []
trajectory_items = []
interaction_items = []
info_items = []
is_running = False
simulation_speed = 5
timer = None
gl_widget = None
stats_label = None
composition_button = None
composition_label = None
initial_energy_spin = None
expansion_rate_spin = None
dark_matter_spin = None
dark_energy_spin = None
baryonic_spin = None
start_btn = None
pause_btn = None
reset_btn = None
speed_slider = None
speed_label = None
interaction_dist_spin = None
fusion_prob_spin = None
structure_prob_spin = None
particle_count_spin = None
show_trajectories = None
show_interaction_effects = None
show_particle_info = None
inflation_checkbox = None
quantum_fluctuations_checkbox = None

app = QApplication(sys.argv)
app.setStyle('Windows')
font = QFont("Arial", 9)
app.setFont(font)
window = QMainWindow()
window.setWindowIcon(QIcon('Icons.ico'))
window.setWindowTitle("宇宙演化模拟器 - 多重宇宙模型")
window.showFullScreen()
central_widget = QWidget()
window.setCentralWidget(central_widget)
main_layout = QHBoxLayout(central_widget)
control_panel = QWidget()
control_panel.setMaximumWidth(350)
control_layout = QVBoxLayout(control_panel)

cosmo_group = QGroupBox("宇宙学参数")
cosmo_layout = QVBoxLayout(cosmo_group)

composition_layout = QHBoxLayout()
composition_button = QPushButton("宇宙组分")
composition_label = QLabel("暗物质/暗能量/重子")
composition_layout.addWidget(QLabel("组分:"))
composition_layout.addWidget(composition_button)
composition_layout.addWidget(composition_label)
composition_layout.addStretch()
cosmo_layout.addLayout(composition_layout)

energy_layout = QHBoxLayout()
initial_energy_spin = QDoubleSpinBox()
initial_energy_spin.setRange(0.1, 10.0)
initial_energy_spin.setValue(3.0)
initial_energy_spin.setSingleStep(0.5)
energy_layout.addWidget(QLabel("初始能量:"))
energy_layout.addWidget(initial_energy_spin)

expansion_rate_spin = QDoubleSpinBox()
expansion_rate_spin.setRange(0.00001, 0.0001)
expansion_rate_spin.setValue(0.00002)
expansion_rate_spin.setSingleStep(0.00001)
energy_layout.addWidget(QLabel("膨胀率:"))
energy_layout.addWidget(expansion_rate_spin)
cosmo_layout.addLayout(energy_layout)

ratio_layout = QHBoxLayout()
dark_matter_spin = QDoubleSpinBox()
dark_matter_spin.setRange(0.0, 1.0)
dark_matter_spin.setValue(0.27)
dark_matter_spin.setSingleStep(0.05)
ratio_layout.addWidget(QLabel("暗物质:"))
ratio_layout.addWidget(dark_matter_spin)

dark_energy_spin = QDoubleSpinBox()
dark_energy_spin.setRange(0.0, 1.0)
dark_energy_spin.setValue(0.68)
dark_energy_spin.setSingleStep(0.05)
ratio_layout.addWidget(QLabel("暗能量:"))
ratio_layout.addWidget(dark_energy_spin)

baryonic_spin = QDoubleSpinBox()
baryonic_spin.setRange(0.0, 1.0)
baryonic_spin.setValue(0.05)
baryonic_spin.setSingleStep(0.05)
ratio_layout.addWidget(QLabel("重子:"))
ratio_layout.addWidget(baryonic_spin)
cosmo_layout.addLayout(ratio_layout)

physics_group = QGroupBox("物理过程")
physics_layout = QVBoxLayout(physics_group)
inflation_checkbox = QCheckBox("宇宙暴胀")
inflation_checkbox.setChecked(False)
quantum_fluctuations_checkbox = QCheckBox("量子涨落")
quantum_fluctuations_checkbox.setChecked(True)
physics_layout.addWidget(inflation_checkbox)
physics_layout.addWidget(quantum_fluctuations_checkbox)

sim_group = QGroupBox("模拟控制")
sim_layout = QVBoxLayout(sim_group)
start_btn = QPushButton("▶ 开始模拟")
pause_btn = QPushButton("⏸ 暂停")
reset_btn = QPushButton("🔄 重置")
speed_slider = QSlider(Qt.Horizontal)
speed_slider.setRange(1, 20)
speed_slider.setValue(5)
speed_label = QLabel("速度: 5x")
sim_layout.addWidget(start_btn)
sim_layout.addWidget(pause_btn)
sim_layout.addWidget(reset_btn)
sim_layout.addWidget(QLabel("模拟速度:"))
sim_layout.addWidget(speed_slider)
sim_layout.addWidget(speed_label)

param_group = QGroupBox("相互作用参数")
param_layout = QVBoxLayout(param_group)
interaction_dist_spin = QDoubleSpinBox()
interaction_dist_spin.setRange(0.1, 2.0)
interaction_dist_spin.setValue(0.5)
interaction_dist_spin.setSingleStep(0.1)
fusion_prob_spin = QDoubleSpinBox()
fusion_prob_spin.setRange(0.0, 1.0)
fusion_prob_spin.setValue(0.1)
fusion_prob_spin.setSingleStep(0.05)
structure_prob_spin = QDoubleSpinBox()
structure_prob_spin.setRange(0.0, 1.0)
structure_prob_spin.setValue(0.05)
structure_prob_spin.setSingleStep(0.02)
particle_count_spin = QSpinBox()
particle_count_spin.setRange(5, 30)
particle_count_spin.setValue(20)

param_layout.addWidget(QLabel("作用距离:"))
param_layout.addWidget(interaction_dist_spin)
param_layout.addWidget(QLabel("核聚变概率:"))
param_layout.addWidget(fusion_prob_spin)
param_layout.addWidget(QLabel("结构形成概率:"))
param_layout.addWidget(structure_prob_spin)
param_layout.addWidget(QLabel("粒子数量:"))
param_layout.addWidget(particle_count_spin)

display_group = QGroupBox("显示选项")
display_layout = QVBoxLayout(display_group)
show_trajectories = QCheckBox("显示粒子轨迹")
show_trajectories.setChecked(True)
show_interaction_effects = QCheckBox("显示相互作用")
show_interaction_effects.setChecked(True)
show_particle_info = QCheckBox("显示宇宙信息")
show_particle_info.setChecked(True)
display_layout.addWidget(show_trajectories)
display_layout.addWidget(show_interaction_effects)
display_layout.addWidget(show_particle_info)

stats_group = QGroupBox("宇宙演化统计")
stats_layout = QVBoxLayout(stats_group)
stats_label = QLabel("宇宙状态将显示在这里...")
stats_label.setWordWrap(True)
stats_layout.addWidget(stats_label)

control_layout.addWidget(cosmo_group)
control_layout.addWidget(physics_group)
control_layout.addWidget(sim_group)
control_layout.addWidget(param_group)
control_layout.addWidget(display_group)
control_layout.addWidget(stats_group)
control_layout.addStretch()

gl_widget = gl.GLViewWidget()
gl_widget.setCameraPosition(distance=20, elevation=25, azimuth=45)
main_layout.addWidget(control_panel)
main_layout.addWidget(gl_widget)


def save_cosmology_config():
    """保存宇宙学配置到.cosmos文件"""
    config = {
        'dark_matter_ratio': simulator_state['dark_matter_ratio'],
        'dark_energy_ratio': simulator_state['dark_energy_ratio'],
        'baryonic_ratio': simulator_state['baryonic_ratio'],
        'initial_energy': simulator_state['initial_energy'],
        'expansion_rate': simulator_state['expansion_rate'],
        'interaction_distance': simulator_state['interaction_distance'],
        'fusion_probability': simulator_state['fusion_probability'],
        'structure_formation_probability': simulator_state['structure_formation_probability'],
        'num_particles': simulator_state['num_particles'],
        'gravitational_constant': simulator_state['gravitational_constant'],
        'cosmic_inflation': simulator_state['cosmic_inflation'],
        'quantum_fluctuations': simulator_state['quantum_fluctuations'],
        'simulation_speed': simulation_speed,
        'show_trajectories': show_trajectories.isChecked(),
        'show_interaction_effects': show_interaction_effects.isChecked(),
        'show_particle_info': show_particle_info.isChecked(),
        'timestamp': datetime.now().isoformat(),
        'simulator_type': 'cosmology_simulator',
        'version': '1.0',
        'description': '宇宙演化模拟器配置文件',
        'universe_model': 'Standard Cosmological Model'
    }

    file_path, _ = QFileDialog.getSaveFileName(
        window,
        "保存宇宙学配置",
        f"Cosmos_Simulation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.cosmos",
        "Cosmos Configuration Files (*.cosmos);;All Files (*)"
    )

    if file_path:
        # 确保文件后缀是.cosmos
        if not file_path.lower().endswith('.cosmos'):
            file_path += '.cosmos'

        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            QMessageBox.information(window, "成功", f"宇宙学配置已保存到:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(window, "错误", f"保存配置失败: {str(e)}")


def load_cosmology_config():
    """从.cosmos文件加载宇宙学配置"""
    if is_running:
        QMessageBox.warning(window, "警告", "请先停止模拟再加载配置")
        return

    file_path, _ = QFileDialog.getOpenFileName(
        window,
        "加载宇宙学配置",
        "",
        "Cosmos Configuration Files (*.cosmos);;All Files (*)"
    )

    if file_path:
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)

            # 验证配置文件类型和版本
            if config.get('simulator_type') != 'cosmology_simulator':
                QMessageBox.warning(
                    window,
                    "文件类型错误",
                    "这不是有效的宇宙模拟器配置文件\n请选择.cosmos格式的文件"
                )
                return

            # 检查版本兼容性
            file_version = config.get('version', '1.0')
            if file_version != '1.0':
                reply = QMessageBox.question(
                    window,
                    "版本警告",
                    f"此配置文件版本 ({file_version}) 可能与当前版本 (1.0) 不兼容\n是否继续加载?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

            # 更新界面控件
            dark_matter_spin.setValue(config.get('dark_matter_ratio', 0.27))
            dark_energy_spin.setValue(config.get('dark_energy_ratio', 0.68))
            baryonic_spin.setValue(config.get('baryonic_ratio', 0.05))
            initial_energy_spin.setValue(config.get('initial_energy', 3.0))
            expansion_rate_spin.setValue(config.get('expansion_rate', 0.00002))
            interaction_dist_spin.setValue(config.get('interaction_distance', 0.5))
            fusion_prob_spin.setValue(config.get('fusion_probability', 0.1))
            structure_prob_spin.setValue(config.get('structure_formation_probability', 0.05))
            particle_count_spin.setValue(config.get('num_particles', 20))
            speed_slider.setValue(config.get('simulation_speed', 5))

            # 更新复选框
            inflation_checkbox.setChecked(config.get('cosmic_inflation', False))
            quantum_fluctuations_checkbox.setChecked(config.get('quantum_fluctuations', True))

            # 更新显示选项
            show_trajectories.setChecked(config.get('show_trajectories', True))
            show_interaction_effects.setChecked(config.get('show_interaction_effects', True))
            show_particle_info.setChecked(config.get('show_particle_info', True))

            # 更新特殊参数
            simulator_state['gravitational_constant'] = config.get('gravitational_constant', 1e-15)

            # 更新状态变量
            update_physics_params()
            update_cosmo_params()
            update_particle_count()
            update_speed(speed_slider.value())

            # 更新组分标签
            composition_label.setText(
                f"DM:{int(dark_matter_spin.value() * 100)}%/DE:{int(dark_energy_spin.value() * 100)}%/B:{int(baryonic_spin.value() * 100)}%")

            # 显示文件信息
            file_info = f"配置文件: {os.path.basename(file_path)}"
            if 'description' in config:
                file_info += f"\n描述: {config['description']}"
            if 'universe_model' in config:
                file_info += f"\n宇宙模型: {config['universe_model']}"
            if 'timestamp' in config:
                file_info += f"\n创建时间: {config['timestamp'][:19]}"

            QMessageBox.information(window, "加载成功", file_info)

        except json.JSONDecodeError:
            QMessageBox.critical(window, "文件错误", "文件格式错误，不是有效的JSON文件")
        except Exception as e:
            QMessageBox.critical(window, "错误", f"加载配置失败: {str(e)}")
def add_cosmology_import_export_buttons():
    """为宇宙模拟器添加导入导出按钮"""
    import_export_group = QGroupBox("配置文件")
    import_export_layout = QHBoxLayout(import_export_group)

    load_btn = QPushButton("📂 导入配置")
    save_btn = QPushButton("💾 导出配置")

    load_btn.clicked.connect(load_cosmology_config)
    save_btn.clicked.connect(save_cosmology_config)

    import_export_layout.addWidget(load_btn)
    import_export_layout.addWidget(save_btn)

    # 插入到控制面板的适当位置
    control_layout.insertWidget(1, import_export_group)
def create_simple_sphere(radius=8.0, slices=16, stacks=8):
    vertices = []
    faces = []

    for i in range(stacks + 1):
        phi = math.pi * i / stacks
        for j in range(slices):
            theta = 2 * math.pi * j / slices
            x = radius * math.sin(phi) * math.cos(theta)
            y = radius * math.sin(phi) * math.sin(theta)
            z = radius * math.cos(phi)
            vertices.append([x, y, z])

    for i in range(stacks):
        for j in range(slices):
            first = i * slices + j
            second = first + slices
            next_j = (j + 1) % slices

            faces.append([first, second, first + 1])
            faces.append([second, second + next_j - j, first + 1])

    return np.array(vertices, dtype=np.float32), np.array(faces, dtype=np.uint32)

sphere_vertices, sphere_faces = create_simple_sphere()

cosmic_sphere = gl.GLMeshItem(
    vertexes=sphere_vertices,
    faces=sphere_faces,
    smooth=False,
    color=(0.1, 0.1, 0.3, 0.05),
    drawEdges=True,
    edgeColor=(0.3, 0.3, 0.5, 0.2),
    glOptions='additive'
)
gl_widget.addItem(cosmic_sphere)

axis_length = 4.0
x_axis = gl.GLLinePlotItem(
    pos=np.array([[0, 0, 0], [axis_length, 0, 0]], dtype=np.float32),
    color=(1, 0, 0, 1), width=2
)
gl_widget.addItem(x_axis)
y_axis = gl.GLLinePlotItem(
    pos=np.array([[0, 0, 0], [0, axis_length, 0]], dtype=np.float32),
    color=(0, 1, 0, 1), width=2
)
gl_widget.addItem(y_axis)
z_axis = gl.GLLinePlotItem(
    pos=np.array([[0, 0, 0], [0, 0, axis_length]], dtype=np.float32),
    color=(0, 0, 1, 1), width=2
)
gl_widget.addItem(z_axis)

timer = QTimer()

def safe_normalize(vector):
    norm = np.linalg.norm(vector)
    if norm == 0 or not np.isfinite(norm) or norm > 1e6:
        return np.array([0.0, 0.0, 0.0], dtype=np.float32)
    return (vector / norm).astype(np.float32)

def safe_distance(pos1, pos2):
    try:
        diff = pos1 - pos2
        if not np.all(np.isfinite(diff)):
            return float('inf')
        distance = np.linalg.norm(diff)
        return distance if np.isfinite(distance) else float('inf')
    except:
        return float('inf')

def clamp_position(position, max_val):
    return np.clip(position, -max_val, max_val).astype(np.float32)

def create_stable_particle(position, momentum, p_type, particle_id):
    particle_mass = cosmology_data[p_type][1]

    position = np.nan_to_num(position, nan=0.0, posinf=3.0, neginf=-3.0).astype(np.float32)
    momentum = np.nan_to_num(momentum, nan=0.0, posinf=0.5, neginf=-0.5).astype(np.float32)

    particle = {
        'particle_id': particle_id,
        'particle_type': p_type,
        'position': position,
        'momentum': momentum,
        'mass': float(particle_mass),
        'charge': cosmology_data[p_type][2],
        'lifetime': cosmology_data[p_type][3],
        'spin': random.choice(["UP", "DOWN", "LEFT", "RIGHT"]),
        'trajectory': [position.copy()],
        'creation_time': 0.0,
        'velocity_history': [],
        'gravitational_charge': float(particle_mass)
    }

    momentum_norm = np.linalg.norm(momentum)
    if not np.isfinite(momentum_norm):
        momentum_norm = 0.0
    energy_sq = momentum_norm ** 2 + particle_mass ** 2
    particle['energy'] = float(math.sqrt(energy_sq) if energy_sq > 0 else 0.001)

    return particle

def initialize_particles():
    particles = []
    particle_counter = 0

    for i in range(simulator_state['num_particles']):
        particle_type_roll = random.random()
        if particle_type_roll < simulator_state['dark_matter_ratio']:
            p_type = "DARK_MATTER"
        elif particle_type_roll < simulator_state['dark_matter_ratio'] + simulator_state['dark_energy_ratio']:
            p_type = "DARK_ENERGY"
        else:
            baryonic_types = ["HYDROGEN", "HELIUM", "PHOTON", "NEUTRINO"]
            p_type = random.choice(baryonic_types)

        theta = random.uniform(0, 2 * math.pi)
        phi = random.uniform(0, math.pi)
        radius = random.uniform(1.0, 5.0)

        position = np.array([
            radius * math.sin(phi) * math.cos(theta),
            radius * math.sin(phi) * math.sin(theta),
            radius * math.cos(phi)
        ], dtype=np.float32)

        momentum_magnitude = random.uniform(0.02, 0.2) * simulator_state['initial_energy']
        momentum = np.array([
            random.gauss(0, 0.05) * momentum_magnitude,
            random.gauss(0, 0.05) * momentum_magnitude,
            random.gauss(0, 0.05) * momentum_magnitude
        ], dtype=np.float32)

        particle = create_stable_particle(position, momentum, p_type, particle_counter)
        particles.append(particle)
        particle_counter += 1

    simulator_state['particles'] = particles
    simulator_state['particle_counter'] = particle_counter

initialize_particles()

def composition_button_click():
    current_ratios = {
        'dark_matter': simulator_state['dark_matter_ratio'],
        'dark_energy': simulator_state['dark_energy_ratio'],
        'baryonic': simulator_state['baryonic_ratio']
    }

    dialog = QDialog(window)
    dialog.setWindowTitle("配置宇宙组分")
    dialog.setModal(True)
    dialog.setFixedSize(400, 300)
    layout = QVBoxLayout()

    info_label = QLabel("调整宇宙能量组分比例 (总和应为1.0)")
    layout.addWidget(info_label)

    dm_layout = QHBoxLayout()
    dm_slider = QSlider(Qt.Horizontal)
    dm_slider.setRange(0, 100)
    dm_slider.setValue(int(current_ratios['dark_matter'] * 100))
    dm_label = QLabel(f"暗物质: {current_ratios['dark_matter']:.2f}")
    dm_layout.addWidget(QLabel("暗物质:"))
    dm_layout.addWidget(dm_slider)
    dm_layout.addWidget(dm_label)

    de_layout = QHBoxLayout()
    de_slider = QSlider(Qt.Horizontal)
    de_slider.setRange(0, 100)
    de_slider.setValue(int(current_ratios['dark_energy'] * 100))
    de_label = QLabel(f"暗能量: {current_ratios['dark_energy']:.2f}")
    de_layout.addWidget(QLabel("暗能量:"))
    de_layout.addWidget(de_slider)
    de_layout.addWidget(de_label)

    ba_layout = QHBoxLayout()
    ba_slider = QSlider(Qt.Horizontal)
    ba_slider.setRange(0, 100)
    ba_slider.setValue(int(current_ratios['baryonic'] * 100))
    ba_label = QLabel(f"重子物质: {current_ratios['baryonic']:.2f}")
    ba_layout.addWidget(QLabel("重子:"))
    ba_layout.addWidget(ba_slider)
    ba_layout.addWidget(ba_label)

    total_label = QLabel(f"总和: 1.00")

    def update_totals():
        total = dm_slider.value() + de_slider.value() + ba_slider.value()
        if total != 100:
            scale = 100.0 / total
            dm_slider.setValue(int(dm_slider.value() * scale))
            de_slider.setValue(int(de_slider.value() * scale))
            ba_slider.setValue(int(ba_slider.value() * scale))

        dm_val = dm_slider.value() / 100.0
        de_val = de_slider.value() / 100.0
        ba_val = ba_slider.value() / 100.0

        dm_label.setText(f"暗物质: {dm_val:.2f}")
        de_label.setText(f"暗能量: {de_val:.2f}")
        ba_label.setText(f"重子物质: {ba_val:.2f}")
        total_label.setText(f"总和: {dm_val + de_val + ba_val:.2f}")

    dm_slider.valueChanged.connect(update_totals)
    de_slider.valueChanged.connect(update_totals)
    ba_slider.valueChanged.connect(update_totals)

    layout.addLayout(dm_layout)
    layout.addLayout(de_layout)
    layout.addLayout(ba_layout)
    layout.addWidget(total_label)

    button_layout = QHBoxLayout()
    ok_button = QPushButton("确定")
    cancel_button = QPushButton("取消")

    def apply_composition():
        simulator_state['dark_matter_ratio'] = dm_slider.value() / 100.0
        simulator_state['dark_energy_ratio'] = de_slider.value() / 100.0
        simulator_state['baryonic_ratio'] = ba_slider.value() / 100.0
        composition_label.setText(f"DM:{dm_slider.value()}%/DE:{de_slider.value()}%/B:{ba_slider.value()}%")
        dialog.accept()

    ok_button.clicked.connect(apply_composition)
    cancel_button.clicked.connect(dialog.reject)
    button_layout.addWidget(ok_button)
    button_layout.addWidget(cancel_button)
    layout.addLayout(button_layout)

    dialog.setLayout(layout)
    dialog.exec_()

def start_simulation():
    global is_running
    if not is_running:
        is_running = True
        timer.start(50 // simulation_speed)
        start_btn.setText("⏵ 运行中...")

def pause_simulation():
    global is_running
    if is_running:
        is_running = False
        timer.stop()
        start_btn.setText("▶ 开始模拟")

def reset_simulation():
    global is_running

    is_running = False
    timer.stop()

    global simulator_state
    simulator_state = initialize_simulator_state()

    simulator_state['interaction_distance'] = interaction_dist_spin.value()
    simulator_state['fusion_probability'] = fusion_prob_spin.value()
    simulator_state['structure_formation_probability'] = structure_prob_spin.value()
    simulator_state['initial_energy'] = initial_energy_spin.value()
    simulator_state['expansion_rate'] = expansion_rate_spin.value()
    simulator_state['dark_matter_ratio'] = dark_matter_spin.value()
    simulator_state['dark_energy_ratio'] = dark_energy_spin.value()
    simulator_state['baryonic_ratio'] = baryonic_spin.value()
    simulator_state['cosmic_inflation'] = inflation_checkbox.isChecked()
    simulator_state['quantum_fluctuations'] = quantum_fluctuations_checkbox.isChecked()
    simulator_state['num_particles'] = particle_count_spin.value()

    initialize_particles()

    for item in particle_items + trajectory_items + interaction_items + info_items:
        gl_widget.removeItem(item)
    particle_items.clear()
    trajectory_items.clear()
    interaction_items.clear()
    info_items.clear()

    start_btn.setText("▶ 开始模拟")

def update_speed(value):
    global simulation_speed
    simulation_speed = value
    speed_label.setText(f"速度: {value}x")
    if is_running:
        timer.start(50 // simulation_speed)

def update_physics_params():
    simulator_state['interaction_distance'] = interaction_dist_spin.value()
    simulator_state['fusion_probability'] = fusion_prob_spin.value()
    simulator_state['structure_formation_probability'] = structure_prob_spin.value()

def update_particle_count():
    if not is_running:
        simulator_state['num_particles'] = particle_count_spin.value()

def update_cosmo_params():
    simulator_state['initial_energy'] = initial_energy_spin.value()
    simulator_state['expansion_rate'] = expansion_rate_spin.value()
    simulator_state['dark_matter_ratio'] = dark_matter_spin.value()
    simulator_state['dark_energy_ratio'] = dark_energy_spin.value()
    simulator_state['baryonic_ratio'] = baryonic_spin.value()
    simulator_state['cosmic_inflation'] = inflation_checkbox.isChecked()
    simulator_state['quantum_fluctuations'] = quantum_fluctuations_checkbox.isChecked()

def update_visualization():
    if not is_running:
        return

    for _ in range(min(simulation_speed, 2)):
        dt = 1e8

        valid_particles = []
        for particle in simulator_state['particles']:
            if (np.all(np.isfinite(particle['position'])) and
                    np.all(np.isfinite(particle['momentum'])) and
                    np.isfinite(particle['energy']) and
                    np.linalg.norm(particle['position']) < 15.0):
                valid_particles.append(particle)

        simulator_state['particles'] = valid_particles

        for particle in simulator_state['particles']:
            if particle['energy'] > 0:
                velocity = particle['momentum'] / particle['energy']
            else:
                velocity = np.array([0.0, 0.0, 0.0], dtype=np.float32)

            velocity = np.nan_to_num(velocity, nan=0.0)

            gravitational_force = np.array([0.0, 0.0, 0.0], dtype=np.float32)

            for other in simulator_state['particles']:
                if other['particle_id'] != particle['particle_id']:
                    r_vec = other['position'] - particle['position']
                    r_mag = safe_distance(particle['position'], other['position'])

                    if (0.3 < r_mag < 6.0 and
                            particle['mass'] > 0 and other['mass'] > 0):

                        force_mag = simulator_state['gravitational_constant'] * particle['mass'] * other['mass'] / (
                                    r_mag ** 2 + 0.1)
                        if np.isfinite(force_mag) and force_mag < 1e8:
                            force_dir = safe_normalize(r_vec)
                            gravitational_force += force_mag * force_dir

            if particle['particle_type'] == "DARK_ENERGY":
                pos_norm = safe_normalize(particle['position'])
                repulsive_force = particle['energy'] * 1e-18 * pos_norm
                gravitational_force -= repulsive_force

            if particle['mass'] > 0:
                acceleration = gravitational_force / (particle['mass'] + 0.001)
                acceleration = np.nan_to_num(acceleration, nan=0.0)
                if np.all(np.abs(acceleration) < 1e8):
                    velocity += acceleration * dt

            velocity = np.clip(velocity, -0.1, 0.1)

            expansion_velocity = simulator_state['expansion_rate'] * particle['position'] * dt * 0.001
            expansion_velocity = np.nan_to_num(expansion_velocity, nan=0.0)

            position_change = (velocity + expansion_velocity) * dt
            position_change = np.clip(position_change, -0.1, 0.1)

            particle['position'] += position_change
            particle['position'] = clamp_position(particle['position'], simulator_state['max_position'])

            if len(particle['trajectory']) > 15:
                particle['trajectory'] = particle['trajectory'][-15:]
            particle['trajectory'].append(particle['position'].copy())

        particles_to_remove = set()
        new_particles = []

        for i in range(len(simulator_state['particles'])):
            if i in particles_to_remove:
                continue
            for j in range(i + 1, len(simulator_state['particles'])):
                if j in particles_to_remove or i in particles_to_remove:
                    continue

                p1, p2 = simulator_state['particles'][i], simulator_state['particles'][j]
                distance = safe_distance(p1['position'], p2['position'])

                if distance > simulator_state['interaction_distance'] or distance == float('inf'):
                    continue

                if (p1['particle_type'] in ["HYDROGEN", "HELIUM"] and
                        p2['particle_type'] in ["HYDROGEN", "HELIUM"] and
                        random.random() < simulator_state['fusion_probability']):

                    total_mass = p1['mass'] + p2['mass']
                    if total_mass > 20.0 and random.random() < 0.05:
                        new_particle_type = "STAR"
                        event_type = "star_formation"
                    else:
                        new_particle_type = "HELIUM" if total_mass > 2.0 else "HYDROGEN"
                        event_type = "nuclear_fusion"

                    new_momentum = (p1['momentum'] + p2['momentum']) * 0.5
                    new_position = (p1['position'] + p2['position']) * 0.5

                    new_particle = create_stable_particle(new_position, new_momentum, new_particle_type,
                                                          simulator_state['particle_counter'])
                    particles_out = [new_particle]

                    event = {
                        'event_id': simulator_state['event_counter'],
                        'particles_in': [p1, p2],
                        'particles_out': particles_out,
                        'position': new_position,
                        'energy': p1['energy'] + p2['energy'],
                        'timestamp': simulator_state['time'],
                        'event_type': event_type
                    }

                    simulator_state['event_counter'] += 1
                    simulator_state['interaction_events'].append(event)
                    particles_to_remove.update([i, j])
                    new_particles.extend(particles_out)
                    simulator_state['particle_counter'] += 1
                    break

        for idx in sorted(particles_to_remove, reverse=True):
            if idx < len(simulator_state['particles']):
                simulator_state['particles'].pop(idx)

        simulator_state['particles'].extend(new_particles)
        simulator_state['time'] += dt
        simulator_state['scale_factor'] *= (1 + simulator_state['expansion_rate'] * dt * 0.001)

    for item in particle_items + trajectory_items + interaction_items + info_items:
        gl_widget.removeItem(item)
    particle_items.clear()
    trajectory_items.clear()
    interaction_items.clear()
    info_items.clear()

    particle_positions = []
    particle_colors = []
    particle_sizes = []

    for particle in simulator_state['particles']:
        if (np.all(np.isfinite(particle['position'])) and
                np.linalg.norm(particle['position']) < 20.0):

            pos = particle['position']
            color = cosmology_data[particle['particle_type']][5]
            size = 3 + math.log(particle['mass'] + 1) * 1.2
            size = min(max(size, 2), 12)

            particle_positions.append(pos)
            particle_colors.append(color)
            particle_sizes.append(size)

            if show_trajectories.isChecked() and len(particle['trajectory']) > 1:
                trajectory = np.array(particle['trajectory'][-6:])
                if (np.all(np.isfinite(trajectory)) and
                        np.all(np.abs(trajectory) < 25.0)):
                    trajectory_item = gl.GLLinePlotItem(
                        pos=trajectory.astype(np.float32),
                        color=color,
                        width=1.2,
                        antialias=True
                    )
                    gl_widget.addItem(trajectory_item)
                    trajectory_items.append(trajectory_item)

    if particle_positions:
        particles_item = gl.GLScatterPlotItem(
            pos=np.array(particle_positions).astype(np.float32),
            color=np.array(particle_colors),
            size=np.array(particle_sizes).astype(np.float32)
        )
        gl_widget.addItem(particles_item)
        particle_items.append(particles_item)

    if show_particle_info.isChecked():
        cosmic_time = simulator_state['time'] / 3.154e7 / 1e9
        stats_text = f"""宇宙演化状态
宇宙年龄: {cosmic_time:.2f} 十亿年
尺度因子: {simulator_state['scale_factor']:.3f}
粒子数: {len(simulator_state['particles'])}
相互作用: {len(simulator_state['interaction_events'])}
模拟速度: {simulation_speed}x"""

        stats_label.setText(stats_text)

composition_button.clicked.connect(composition_button_click)
start_btn.clicked.connect(start_simulation)
pause_btn.clicked.connect(pause_simulation)
reset_btn.clicked.connect(reset_simulation)
speed_slider.valueChanged.connect(update_speed)
interaction_dist_spin.valueChanged.connect(update_physics_params)
fusion_prob_spin.valueChanged.connect(update_physics_params)
structure_prob_spin.valueChanged.connect(update_physics_params)
particle_count_spin.valueChanged.connect(update_particle_count)
initial_energy_spin.valueChanged.connect(update_cosmo_params)
expansion_rate_spin.valueChanged.connect(update_cosmo_params)
dark_matter_spin.valueChanged.connect(update_cosmo_params)
dark_energy_spin.valueChanged.connect(update_cosmo_params)
baryonic_spin.valueChanged.connect(update_cosmo_params)
inflation_checkbox.stateChanged.connect(update_cosmo_params)
quantum_fluctuations_checkbox.stateChanged.connect(update_cosmo_params)
timer.timeout.connect(update_visualization)

window.show()
add_cosmology_import_export_buttons()
sys.exit(app.exec_())