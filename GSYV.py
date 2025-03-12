"""
pyinstaller -F -w --add-data "/Users/chawresh/Desktop/files:files" --icon "/Users/chawresh/Desktop/logo.icns" --name "GSYV" GSYV.py
"""
import sys
import sqlite3
import json
import pandas as pd
import qtawesome as qta
import platform
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QGroupBox,
                             QFileDialog, QInputDialog, QLabel, QMessageBox, QDialog,
                             QFormLayout, QDialogButtonBox, QComboBox, QTextEdit,
                             QTabWidget, QMenu, QSpinBox, QCheckBox, QAbstractItemView, QDateEdit,
                             QListWidget, QListWidgetItem)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QPixmap, QTextOption
import os
import shutil
import logging
import glob
import time
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import mplcursors

# Log ayarları
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
FILES_DIR = os.path.join(BASE_DIR, "files")
os.makedirs(FILES_DIR, exist_ok=True)
logging.basicConfig(filename=os.path.join(FILES_DIR, 'inventory.log'),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sabitler
GROUPS_FILE = os.path.join(FILES_DIR, "groups.json")
CONFIG_FILE = os.path.join(FILES_DIR, "config.json")
DB_FILE = os.path.join(FILES_DIR, "inventory.db")
LOGO_FILE = os.path.join(FILES_DIR, "logo.png")
USERS_FILE = os.path.join(FILES_DIR, "users.json")
REGIONS_FILE = os.path.join(FILES_DIR, "regions.json")
FLOORS_FILE = os.path.join(FILES_DIR, "floors.json")

# Türkçe çeviriler
TRANSLATIONS = {
    "title": "GALATASARAYLILAR YURDU Envanter Kayıt Sistemi",
    "inventory_tab": "Envanter Kayıt",
    "settings_tab": "Ayarlar",
    "about_tab": "Hakkında",
    "archive_tab": "Arşiv",
    "add_item": "Ekle",
    "edit_item": "Düzenle",
    "archive_item": "Arşive Taşı",
    "delete_item": "Sil",
    "duplicate_item": "Çoğalt",
    "show_details": "Detay Göster",
    "view_item": "Görüntüle",
    "restore_item": "Geri Yükle",
    "tools": "Araçlar",
    "close_item": "Kapat",
    "export_excel": "Excel'e Aktar",
    "import_excel": "Excel'den İçe Aktar",
    "generate_pdf": "PDF Rapor Oluştur",
    "error_all_fields": "Tüm alanlar doldurulmalıdır!",
    "error_select_row": "Lütfen bir satır seçin!",
    "confirm_archive": "Bu envanteri arşive taşımak istediğinizden emin misiniz?",
    "confirm_delete": "Bu envanteri silmek istediğinizden emin misiniz?",
    "confirm_delete_final": "Bu işlem geri alınamaz! Silmeyi onaylıyor musunuz?",
    "item_added": "Yeni envanter eklendi!",
    "item_updated": "Envanter güncellendi!",
    "item_archived": "Envanter arşive taşındı!",
    "item_deleted": "Envanter silindi!",
    "item_restored": "Envanter geri yüklendi!",
    "db_backed_up": "Veritabanı yedeklendi!",
    "about_description": "Bu uygulama, GALATASARAYLILAR YURDU envanterini etkili bir şekilde yönetmek ve takip etmek için geliştirilmiştir.",
    "about_copyright": "© 2025 Mustafa AKBAL. Tüm hakları saklıdır.",
    "backup_frequency": "Yedekleme Sıklığı (dakika):",
    "default_group": "Varsayılan Grup:",
    "excel_exported": "Veriler Excel'e aktarıldı!",
    "excel_imported": "Veriler Excel'den içe aktarıldı!",
    "pdf_generated": "PDF raporu oluşturuldu!",
    "details_title": "Envanter Detayları",
    "select_section": "Eklenecek Bölüm Seçin:",
    "add_parameter": "Yeni Parametre Ekle",
    "delete_parameter": "Parametre Sil",
    "edit_parameter": "Parametre Düzenle",
    "manual_backup": "Manuel Yedekleme",
    "data_analysis": "Veri Analizi",
    "param_management": "Parametre Yönetimi",
    "backup_operations": "Yedekleme İşlemleri",
    "analysis_title": "Veri Analizi",
    "total_records": "Toplam Kayıt Sayısı: {}",
    "group_distribution": "Grup Dağılımı:",
    "search_placeholder": "Tabloda Ara...",
    "filter_group": "Gruba Göre Filtrele:",
    "font_size": "Yazı Boyutu:",
    "backup_path": "Yedekleme Konumu:",
    "backup_retention": "Yedekleme Saklama Süresi (Gün):",
    "autosave_interval": "Otomatik Kaydetme Aralığı (dakika):",
    "export_format": "Varsayılan Dışa Aktarma Formatı:",
    "reset_settings": "Ayarları Sıfırla",
    "startup_group": "Başlangıç Grubu:",
    "card_info": "Kart Bilgileri",
    "invoice_info": "Fatura Bilgileri",
    "service_info": "Servis Bilgileri",
    "group_name": "Grup Adı",
    "item_name": "Envanter Adı",
    "purchase_date": "Alış Tarihi",
    "purchase_cost": "Alış Bedeli",
    "cost_center": "Masraf Merkezi",
    "warranty_period": "Garanti Süresi",
    "invoice_no": "Fatura No",
    "quantity": "Adet",
    "company": "Firma",
    "description": "Açıklama",
    "brand": "Marka",
    "model": "Model",
    "last_updated": "Son Güncelleme",
    "user": "Kullanan Kişi",
    "region": "Bölge veya Oda",
    "floor": "Kat",
    "edit_groups": "Grup Düzenle",
    "edit_users": "Kullanıcı Düzenle",
    "edit_regions": "Bölge veya Oda Düzenle",
    "edit_floors": "Kat Düzenle",
    "combobox_management": "ComboBox Yönetimi",
    "add_new_item": "Yeni Ekle",
    "edit_selected_item": "Seçileni Düzenle",
    "delete_selected_item": "Seçileni Sil",
    "status": "Durum",
    "note": "Not",
    "unknown": "Bilinmiyor"  # Yeni eklenen çeviri
}

DEFAULT_GROUPS = [
    {"name": "Genel", "code": "GEN"},
    {"name": "Mobilya", "code": "MOB"},
    {"name": "Mutfak", "code": "MUT"},
    {"name": "Elektronik", "code": "ELK"},
    {"name": "Bakım Malzemesi", "code": "BAK"},
    {"name": "Temizlik", "code": "TEM"}
]
DEFAULT_USERS = [{"name": "Müdür", "code": "MDR"}, {"name": "Güvenlik", "code": "GVN"}, {"name": "Sosyal Hizmet", "code": "SOS"}]
DEFAULT_REGIONS = [{"name": "Salon", "code": "SAL"}, {"name": "Mutfak", "code": "MUT"}, {"name": "Müdür Odası", "code": "MOD"}, {"name": "Teras", "code": "TER"}]
DEFAULT_FLOORS = [
    {"name": "Kat -2", "code": "K-2"},
    {"name": "Kat -1", "code": "K-1"},
    {"name": "Kat 0", "code": "K00"},
    {"name": "Kat 1", "code": "K01"},
    {"name": "Kat 2", "code": "K02"},
    {"name": "Kat 3", "code": "K03"},
    {"name": "Kat 4", "code": "K04"},
    {"name": "Kat 5", "code": "K05"}
]

class AddParameterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSLATIONS["add_parameter"])
        self.entries = {}
        self.sections = ["Kart Bilgileri", "Fatura Bilgileri", "Servis Bilgileri"]

        layout = QFormLayout(self)
        label = QLabel("Parametre Adı *")
        entry = QLineEdit()
        entry.setPlaceholderText("Ör: Bakım Durumu")
        self.entries["Parameter Name"] = entry
        layout.addRow(label, entry)

        section_label = QLabel(TRANSLATIONS["select_section"])
        self.section_combo = QComboBox()
        self.section_combo.addItems(self.sections)
        layout.addRow(section_label, self.section_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return self.entries["Parameter Name"].text().strip(), self.section_combo.currentText()

class ColumnSelectionDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("PDF için Sütun Seç")
        self.headers = headers
        self.selected_columns = []

        layout = QVBoxLayout(self)
        self.checkboxes = {}

        for header in headers:
            checkbox = QCheckBox(header)
            checkbox.setChecked(True)
            self.checkboxes[header] = checkbox
            layout.addWidget(checkbox)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_selected_columns(self):
        self.selected_columns = [header for header, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        return self.selected_columns

class EditParameterDialog(QDialog):
    def __init__(self, parent=None, current_name=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSLATIONS["edit_parameter"])
        self.parent = parent
        self.current_name = current_name
        self.sections = ["Kart Bilgileri", "Fatura Bilgileri", "Servis Bilgileri"]

        layout = QFormLayout(self)
        label = QLabel("Yeni Parametre Adı *")
        self.name_entry = QLineEdit(current_name)
        layout.addRow(label, self.name_entry)

        section_label = QLabel(TRANSLATIONS["select_section"])
        self.section_combo = QComboBox()
        self.section_combo.addItems(self.sections)
        if self.parent.conn:
            cursor = self.parent.conn.cursor()
            cursor.execute("SELECT section FROM metadata WHERE column_name = ?", (current_name,))
            current_section = cursor.fetchone()
            if current_section:
                self.section_combo.setCurrentText(current_section[0])
        layout.addRow(section_label, self.section_combo)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        return self.name_entry.text().strip(), self.section_combo.currentText()

class ComboBoxEditDialog(QDialog):
    def __init__(self, parent=None, title="", items=None, file_path=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.parent = parent
        self.items = items.copy()
        self.file_path = file_path

        layout = QVBoxLayout(self)
        self.list_widget = QListWidget()
        for item in self.items:
            self.list_widget.addItem(QListWidgetItem(item["name"]))
        layout.addWidget(self.list_widget)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton(TRANSLATIONS["add_new_item"])
        self.add_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton(TRANSLATIONS["edit_selected_item"])
        self.edit_button.clicked.connect(self.edit_item)
        button_layout.addWidget(self.edit_button)

        self.delete_button = QPushButton(TRANSLATIONS["delete_selected_item"])
        self.delete_button.clicked.connect(self.delete_item)
        button_layout.addWidget(self.delete_button)

        layout.addLayout(button_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def add_item(self):
        new_item, ok = QInputDialog.getText(self, "Yeni Öğe Ekle", "Yeni öğe adını girin:")
        if ok and new_item.strip() and not any(item["name"] == new_item.strip() for item in self.items):
            shortcode = self.parent.generate_shortcode(new_item.strip(), [item["code"] for item in self.items])
            self.items.append({"name": new_item.strip(), "code": shortcode})
            self.list_widget.addItem(QListWidgetItem(new_item.strip()))
            self.save_items()

    def edit_item(self):
        selected = self.list_widget.currentItem()
        if selected:
            old_item = selected.text()
            new_item, ok = QInputDialog.getText(self, "Öğe Düzenle", "Yeni adı girin:", text=old_item)
            if ok and new_item.strip() and new_item.strip() != old_item:
                for item in self.items:
                    if item["name"] == old_item:
                        item["name"] = new_item.strip()
                        break
                selected.setText(new_item.strip())
                self.save_items()

    def delete_item(self):
        selected = self.list_widget.currentItem()
        if selected:
            item = selected.text()
            if QMessageBox.question(self, "Silme Onayı", f"'{item}' öğesini silmek istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.items[:] = [i for i in self.items if i["name"] != item]
                self.list_widget.takeItem(self.list_widget.row(selected))
                self.save_items()

    def save_items(self):
        with open(self.file_path, 'w', encoding='utf-8') as f:
            json.dump(self.items, f, ensure_ascii=False, indent=4)
        self.parent.update_comboboxes()

class EditDialog(QDialog):
    def __init__(self, parent=None, row_data=None, headers=None):
        super().__init__(parent)
        self.setWindowTitle("Envanter Düzenle")
        self.parent = parent
        self.row_data = row_data
        self.headers = headers
        self.entries = {}

        layout = QFormLayout(self)
        for i, header in enumerate(self.headers):
            label = QLabel(header)
            if header == "Kod":
                entry = QLineEdit(self.row_data[i])
                entry.setReadOnly(True)
                self.entries[header] = entry
            elif header == TRANSLATIONS["group_name"]:
                combo = QComboBox()
                combo.addItems([item["name"] for item in self.parent.groups])
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header == TRANSLATIONS["region"]:
                combo = QComboBox()
                combo.addItems([item["name"] for item in self.parent.regions])
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header == TRANSLATIONS["floor"]:
                combo = QComboBox()
                combo.addItems([item["name"] for item in self.parent.floors])
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header == TRANSLATIONS["user"]:
                combo = QComboBox()
                combo.addItems([item["name"] for item in self.parent.users])
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header == TRANSLATIONS["purchase_date"]:
                date_layout = QHBoxLayout()
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                try:
                    if self.row_data[i] != TRANSLATIONS["unknown"]:
                        date_edit.setDate(datetime.strptime(self.row_data[i], "%d.%m.%Y"))
                    else:
                        date_edit.setDate(datetime.now().date())
                except ValueError:
                    date_edit.setDate(datetime.now().date())
                self.entries[header] = date_edit
                unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                unknown_check.setChecked(self.row_data[i] == TRANSLATIONS["unknown"])
                unknown_check.stateChanged.connect(lambda state, de=date_edit: self.toggle_date(de, state))
                date_layout.addWidget(date_edit)
                date_layout.addWidget(unknown_check)
                self.entries[f"{header}_check"] = unknown_check
                layout.addRow(label, date_layout)
                continue
            elif header == TRANSLATIONS["warranty_period"]:
                date_layout = QHBoxLayout()
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                try:
                    if self.row_data[i] != TRANSLATIONS["unknown"]:
                        date_edit.setDate(datetime.strptime(self.row_data[i], "%d.%m.%Y"))
                    else:
                        date_edit.setDate(datetime.now().date())
                except ValueError:
                    date_edit.setDate(datetime.now().date())
                self.entries[header] = date_edit
                unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                unknown_check.setChecked(self.row_data[i] == TRANSLATIONS["unknown"])
                unknown_check.stateChanged.connect(lambda state, de=date_edit: self.toggle_date(de, state))
                date_layout.addWidget(date_edit)
                date_layout.addWidget(unknown_check)
                self.entries[f"{header}_check"] = unknown_check
                layout.addRow(label, date_layout)
                continue
            elif header in [TRANSLATIONS["note"], TRANSLATIONS["description"]]:
                entry = QTextEdit(self.row_data[i])
                entry.setAcceptRichText(False)
                entry.setMaximumHeight(75)
                self.entries[header] = entry
            else:
                entry = QLineEdit(self.row_data[i])
                self.entries[header] = entry
            layout.addRow(label, self.entries[header])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.setMinimumSize(600, 400)
        self.resize(800, 800)

    def toggle_date(self, date_edit, state):
        date_edit.setEnabled(state == Qt.Unchecked)

    def get_data(self):
        data = []
        for header in self.headers:
            if header in self.entries:
                if isinstance(self.entries[header], QComboBox):
                    value = self.entries[header].currentText()
                elif isinstance(self.entries[header], QDateEdit):
                    if f"{header}_check" in self.entries and self.entries[f"{header}_check"].isChecked():
                        value = TRANSLATIONS["unknown"]
                    else:
                        value = self.entries[header].date().toString("dd.MM.yyyy")
                elif isinstance(self.entries[header], QTextEdit):
                    value = self.entries[header].toPlainText()
                else:
                    value = self.entries[header].text()
                data.append(value)
        return data

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.os_name = platform.system()
        self.default_font = "Helvetica"
        font_path = os.path.join(FILES_DIR, "DejaVuSans.ttf")

        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                self.default_font = "DejaVuSans"
                logging.info(f"DejaVuSans.ttf başarıyla yüklendi: {font_path}")
                plt.rcParams['font.family'] = 'DejaVuSans'
            else:
                pdfmetrics.registerFont(TTFont("Helvetica", "Helvetica"))
                logging.warning(f"DejaVuSans.ttf bulunamadı: {font_path}, Helvetica kullanılıyor.")
                plt.rcParams['font.family'] = 'Helvetica'
        except Exception as e:
            logging.error(f"Font kaydı hatası: {str(e)}. Helvetica kullanılıyor.")
            self.default_font = "Helvetica"
            plt.rcParams['font.family'] = 'Helvetica'

        self.setWindowTitle(TRANSLATIONS["title"])
        self.setGeometry(100, 100, 1200, 700)

        os.makedirs(FILES_DIR, exist_ok=True)

        self.db_exists = os.path.exists(DB_FILE)
        if self.db_exists:
            self.conn = sqlite3.connect(DB_FILE)
            logging.info("Mevcut veritabanı bulundu ve bağlanıldı.")
        else:
            self.conn = sqlite3.connect(DB_FILE)
            self.db_exists = True
            logging.info("Veritabanı bulunamadı, yeni bir veritabanı oluşturuldu.")
        self.create_or_update_tables()

        self.load_config()
        self.groups = self.load_json_data(GROUPS_FILE, DEFAULT_GROUPS)
        self.users = self.load_json_data(USERS_FILE, DEFAULT_USERS)
        self.regions = self.load_json_data(REGIONS_FILE, DEFAULT_REGIONS)
        self.floors = self.load_json_data(FLOORS_FILE, DEFAULT_FLOORS)

        self.main_widget = QWidget()
        self.setCentralWidget(self.main_widget)
        self.layout = QVBoxLayout(self.main_widget)

        self.tabs = QTabWidget()
        self.tabs.addTab(QWidget(), qta.icon('fa5s.table', color='#D32F2F'), TRANSLATIONS["inventory_tab"])
        self.tabs.addTab(QWidget(), qta.icon('fa5s.archive', color='#D32F2F'), TRANSLATIONS["archive_tab"])
        self.tabs.addTab(QWidget(), qta.icon('fa5s.cog', color='#D32F2F'), TRANSLATIONS["settings_tab"])
        self.tabs.addTab(QWidget(), qta.icon('fa5s.info-circle', color='#D32F2F'), TRANSLATIONS["about_tab"])
        self.layout.addWidget(self.tabs)

        self.inventory_tab = self.tabs.widget(0)
        self.archive_tab = self.tabs.widget(1)
        self.settings_tab = self.tabs.widget(2)
        self.about_tab = self.tabs.widget(3)

        self.inventory_tab.setLayout(QVBoxLayout())
        self.archive_tab.setLayout(QVBoxLayout())
        self.settings_tab.setLayout(QVBoxLayout())
        self.about_tab.setLayout(QVBoxLayout())

        self.setup_inventory_tab()
        self.setup_archive_tab()
        self.setup_settings_tab()
        self.setup_about_tab()

        self.load_data_from_db()
        self.load_archive_from_db()

        self.backup_timer = QTimer(self)
        self.backup_timer.timeout.connect(self.auto_backup)
        self.backup_timer.start(self.config["backup_frequency"] * 60000)

        self.autosave_timer = QTimer(self)
        self.autosave_timer.timeout.connect(self.save_current_form)
        self.autosave_timer.start(self.config["autosave_interval"] * 60000)

        self.change_font_size(self.config["font_size"])

    def load_json_data(self, file_path, default_data):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"{file_path} yüklenirken hata: {str(e)}")
        return default_data

    def save_json_data(self, file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logging.error(f"{file_path} kaydedilirken hata: {str(e)}")

    def generate_shortcode(self, name, existing_codes):
        shortcode = name[:3].upper()
        if shortcode in existing_codes:
            i = 1
            while f"{shortcode}{i}" in existing_codes:
                i += 1
            shortcode = f"{shortcode}{i}"
        return shortcode

    def update_json_with_shortcode(self, param_name, json_data, file_path, action="add"):
        if action == "add":
            if not any(item["name"] == param_name for item in json_data):
                shortcode = self.generate_shortcode(param_name, [item["code"] for item in json_data])
                json_data.append({"name": param_name, "code": shortcode})
                self.save_json_data(file_path, json_data)
                logging.info(f"{param_name} için {shortcode} kısaltması {file_path} dosyasına eklendi.")
        elif action == "delete":
            json_data[:] = [item for item in json_data if item["name"] != param_name]
            self.save_json_data(file_path, json_data)
            logging.info(f"{param_name} ve kısaltması {file_path} dosyasından silindi.")

    def add_new_combo_item(self, combo_box, data_list, file_path):
        new_item = combo_box.currentText().strip()
        if new_item and not any(item["name"] == new_item for item in data_list):
            shortcode = self.generate_shortcode(new_item, [item["code"] for item in data_list])
            data_list.append({"name": new_item, "code": shortcode})
            combo_box.addItem(new_item)
            self.save_json_data(file_path, data_list)
            self.update_comboboxes()
            logging.info(f"Yeni öğe '{new_item}' {file_path} dosyasına eklendi.")

    def update_comboboxes(self):
        if hasattr(self, 'group_combo'):
            self.group_combo.clear()
            self.group_combo.addItems([item["name"] for item in self.groups])
        if TRANSLATIONS["user"] in self.card_entries:
            self.card_entries[TRANSLATIONS["user"]].clear()
            self.card_entries[TRANSLATIONS["user"]].addItems([item["name"] for item in self.users])
        if TRANSLATIONS["region"] in self.card_entries:
            self.card_entries[TRANSLATIONS["region"]].clear()
            self.card_entries[TRANSLATIONS["region"]].addItems([item["name"] for item in self.regions])
        if TRANSLATIONS["floor"] in self.card_entries:
            self.card_entries[TRANSLATIONS["floor"]].clear()
            self.card_entries[TRANSLATIONS["floor"]].addItems([item["name"] for item in self.floors])
        if hasattr(self, 'default_group_combo'):
            self.default_group_combo.clear()
            self.default_group_combo.addItems([item["name"] for item in self.groups])
        if hasattr(self, 'startup_group_combo'):
            self.startup_group_combo.clear()
            self.startup_group_combo.addItems([item["name"] for item in self.groups] + ["Son Kullanılan"])
        if hasattr(self, 'filter_combo'):
            self.filter_combo.clear()
            self.filter_combo.addItem("Tümü")
            self.filter_combo.addItems([item["name"] for item in self.groups])

    def get_widget_value(self, widget):
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QDateEdit):
            return widget.date().toString("dd.MM.yyyy")
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText()
        elif hasattr(widget, 'text'):
            return widget.text()
        return ""

    def generate_inventory_code(self, group_name, region_name, floor_name):
        def get_or_add_code(item_list, file_path, name, existing_codes):
            item = next((item for item in item_list if item["name"] == name), None)
            if not item:
                shortcode = self.generate_shortcode(name, existing_codes)
                item = {"name": name, "code": shortcode}
                item_list.append(item)
                self.save_json_data(file_path, item_list)
                logging.info(f"Yeni öğe '{name}' için '{shortcode}' kodu {file_path} dosyasına eklendi.")
            return item["code"]

        def format_floor_code(floor_name):
            if "Kat" in floor_name:
                floor_num = floor_name.replace("Kat ", "").strip()
                try:
                    num = int(floor_num)
                    if num < 0:
                        return f"KE{abs(num)}"
                    elif num == 0:
                        return "K00"
                    else:
                        return f"K{num:02d}"
                except ValueError:
                    pass
            return floor_name[:3].upper()

        group_code = get_or_add_code(self.groups, GROUPS_FILE, group_name, [item["code"] for item in self.groups])
        region_code = get_or_add_code(self.regions, REGIONS_FILE, region_name, [item["code"] for item in self.regions])
        floor_code = get_or_add_code(self.floors, FLOORS_FILE, floor_name, [item["code"] for item in self.floors])

        floor_item = next((item for item in self.floors if item["name"] == floor_name), None)
        if floor_item:
            floor_item["code"] = format_floor_code(floor_name)
            self.save_json_data(FLOORS_FILE, self.floors)

        code = f"{group_code}-{region_code}-{floor_item['code']}"
        return code

    def decode_inventory_code(self, code):
        try:
            if not code or "-" not in code:
                return "Geçersiz kod formatı! Kod, GRUP-BÖLGE-KAT formatında olmalıdır."
            
            parts = code.split("-")
            if len(parts) != 3:
                return f"Hatalı kod formatı: '{code}' (Beklenen: GRUP-BÖLGE-KAT)."

            group_code, region_code, floor_code = parts

            if not group_code or not region_code or not floor_code:
                return f"Hatalı kod formatı: '{code}' (Boş kısaltma)."

            group_name = next((item["name"] for item in self.groups if item["code"] == group_code), "Bilinmeyen Grup")
            region_name = next((item["name"] for item in self.regions if item["code"] == region_code), "Bilinmeyen Bölge")

            if floor_code.startswith("KE"):
                try:
                    floor_num = -int(floor_code[2:])
                    floor_name = f"Kat {floor_num}"
                except ValueError:
                    floor_name = "Bilinmeyen Kat"
            else:
                floor_name = next((item["name"] for item in self.floors if item["code"] == floor_code), "Bilinmeyen Kat")
            
            if "Bilinmeyen" in [group_name, region_name, floor_name]:
                return f"Kod çözümleme başarısız: '{code}'. Grup: {group_name}, Bölge: {region_name}, Kat: {floor_name}."

            return f"Grup: {group_name}, Bölge: {region_name}, Kat: {floor_name}"
        except Exception as e:
            logging.error(f"Kod çözümleme hatası: {str(e)}, Kod: {code}")
            return f"Kod çözümleme hatası: {str(e)}"

    def setup_inventory_tab(self):
        if self.inventory_tab.layout() is not None:
            while self.inventory_tab.layout().count():
                child = self.inventory_tab.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.inventory_tab.setLayout(QVBoxLayout())

        layout = self.inventory_tab.layout()
        top_layout = QHBoxLayout()

        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name, section FROM metadata ORDER BY column_order")
        metadata = cursor.fetchall()
        if not metadata:
            self.create_or_update_tables()
            cursor.execute("SELECT column_name, section FROM metadata ORDER BY column_order")
            metadata = cursor.fetchall()

        card_headers = [name for name, section in metadata if section == TRANSLATIONS["card_info"]]
        invoice_headers = [name for name, section in metadata if section == TRANSLATIONS["invoice_info"]]
        service_headers = [name for name, section in metadata if section == TRANSLATIONS["service_info"]]

        self.card_group = QGroupBox(TRANSLATIONS["card_info"])
        self.card_layout = QFormLayout()
        self.card_entries = {}
        for header in card_headers:
            label = QLabel(header + (" *" if header == TRANSLATIONS["item_name"] else ""))
            if header == "Kod":
                entry = QLineEdit("Otomatik")
                entry.setReadOnly(True)
                self.card_entries[header] = entry
            elif header == TRANSLATIONS["group_name"]:
                self.group_combo = QComboBox()
                self.group_combo.addItems([item["name"] for item in self.groups])
                self.group_combo.setEditable(True)
                self.group_combo.lineEdit().returnPressed.connect(lambda: self.add_new_combo_item(self.group_combo, self.groups, GROUPS_FILE))
                self.card_entries[header] = self.group_combo
                if self.config["startup_group"] != "Son Kullanılan" and self.config["startup_group"] in [item["name"] for item in self.groups]:
                    self.group_combo.setCurrentText(self.config["startup_group"])
            elif header == TRANSLATIONS["purchase_date"]:
                date_layout = QHBoxLayout()
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                date_edit.setDate(datetime.now().date())
                self.card_entries[header] = date_edit
                unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                unknown_check.stateChanged.connect(lambda state, de=date_edit: de.setEnabled(state == Qt.Unchecked))
                date_layout.addWidget(date_edit)
                date_layout.addWidget(unknown_check)
                self.card_entries[f"{header}_check"] = unknown_check
                self.card_layout.addRow(label, date_layout)
                continue
            elif header == TRANSLATIONS["user"]:
                user_combo = QComboBox()
                user_combo.addItems([item["name"] for item in self.users])
                user_combo.setEditable(True)
                user_combo.lineEdit().returnPressed.connect(lambda: self.add_new_combo_item(user_combo, self.users, USERS_FILE))
                self.card_entries[header] = user_combo
            elif header == TRANSLATIONS["region"]:
                region_combo = QComboBox()
                region_combo.addItems([item["name"] for item in self.regions])
                region_combo.setEditable(True)
                region_combo.lineEdit().returnPressed.connect(lambda: self.add_new_combo_item(region_combo, self.regions, REGIONS_FILE))
                self.card_entries[header] = region_combo
            elif header == TRANSLATIONS["floor"]:
                floor_combo = QComboBox()
                floor_combo.addItems([item["name"] for item in self.floors])
                floor_combo.setEditable(True)
                floor_combo.lineEdit().returnPressed.connect(lambda: self.add_new_combo_item(floor_combo, self.floors, FLOORS_FILE))
                self.card_entries[header] = floor_combo
            else:
                entry = QLineEdit()
                self.card_entries[header] = entry
            self.card_layout.addRow(label, self.card_entries[header])
        self.card_group.setLayout(self.card_layout)
        top_layout.addWidget(self.card_group)

        self.invoice_group = QGroupBox(TRANSLATIONS["invoice_info"])
        self.invoice_layout = QFormLayout()
        self.invoice_entries = {}
        for key in invoice_headers:
            label = QLabel(key)
            entry = QLineEdit()
            self.invoice_entries[key] = entry
            self.invoice_layout.addRow(label, entry)
        self.invoice_group.setLayout(self.invoice_layout)
        top_layout.addWidget(self.invoice_group)

        self.service_group = QGroupBox(TRANSLATIONS["service_info"])
        self.service_layout = QFormLayout()
        self.service_entries = {}
        for key in service_headers:
            label = QLabel(key)
            if key == TRANSLATIONS["warranty_period"]:
                date_layout = QHBoxLayout()
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                date_edit.setDate(datetime.now().date())
                self.service_entries[key] = date_edit
                unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                unknown_check.stateChanged.connect(lambda state, de=date_edit: de.setEnabled(state == Qt.Unchecked))
                date_layout.addWidget(date_edit)
                date_layout.addWidget(unknown_check)
                self.service_entries[f"{key}_check"] = unknown_check
                self.service_layout.addRow(label, date_layout)
            elif key == TRANSLATIONS["note"]:
                entry = QTextEdit()
                entry.setMaximumHeight(60)
                entry.setAcceptRichText(False)
                self.service_entries[key] = entry
                self.service_layout.addRow(label, entry)
            else:
                entry = QLineEdit()
                self.service_entries[key] = entry
                self.service_layout.addRow(label, entry)
        self.service_group.setLayout(self.service_layout)
        top_layout.addWidget(self.service_group)

        layout.addLayout(top_layout)

        search_filter_layout = QHBoxLayout()
        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText(TRANSLATIONS["search_placeholder"])
        self.search_bar.textChanged.connect(self.quick_search)
        search_filter_layout.addWidget(self.search_bar)

        self.filter_combo = QComboBox()
        self.filter_combo.addItem("Tümü")
        self.filter_combo.addItems([item["name"] for item in self.groups])
        self.filter_combo.currentTextChanged.connect(self.filter_data)
        search_filter_layout.addWidget(QLabel(TRANSLATIONS["filter_group"]))
        search_filter_layout.addWidget(self.filter_combo)
        layout.addLayout(search_filter_layout)

        self.table = QTableWidget()
        all_headers = self.get_column_headers() + [TRANSLATIONS["last_updated"]]
        self.table.setColumnCount(len(all_headers))
        self.table.setHorizontalHeaderLabels(all_headers)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemDoubleClicked.connect(self.open_edit_dialog)
        layout.addWidget(self.table)

        button_layout = QHBoxLayout()
        self.add_button = QPushButton(TRANSLATIONS["add_item"])
        self.add_button.setIcon(qta.icon('fa5s.plus', color='#FFC107'))
        self.add_button.clicked.connect(self.add_item)
        button_layout.addWidget(self.add_button)

        self.edit_button = QPushButton(TRANSLATIONS["edit_item"])
        self.edit_button.setIcon(qta.icon('fa5s.edit', color='#FFC107'))
        self.edit_button.clicked.connect(self.open_edit_dialog)
        button_layout.addWidget(self.edit_button)

        self.archive_button = QPushButton(TRANSLATIONS["archive_item"])
        self.archive_button.setIcon(qta.icon('fa5s.archive', color='#D32F2F'))
        self.archive_button.clicked.connect(self.archive_item_with_confirmation)
        button_layout.addWidget(self.archive_button)

        self.delete_button = QPushButton(TRANSLATIONS["delete_item"])
        self.delete_button.setIcon(qta.icon('fa5s.trash', color='#D32F2F'))
        self.delete_button.clicked.connect(self.delete_item_with_double_confirmation)
        button_layout.addWidget(self.delete_button)

        self.duplicate_button = QPushButton(TRANSLATIONS["duplicate_item"])
        self.duplicate_button.setIcon(qta.icon('fa5s.copy', color='#FFC107'))
        self.duplicate_button.clicked.connect(self.duplicate_item)
        button_layout.addWidget(self.duplicate_button)

        self.detail_button = QPushButton(TRANSLATIONS["show_details"])
        self.detail_button.setIcon(qta.icon('fa5s.info', color='#D32F2F'))
        self.detail_button.clicked.connect(self.show_details)
        button_layout.addWidget(self.detail_button)

        self.export_excel_button = QPushButton(TRANSLATIONS["export_excel"])
        self.export_excel_button.setIcon(qta.icon('fa5s.file-excel', color='#FFC107'))
        self.export_excel_button.clicked.connect(self.export_to_file)
        button_layout.addWidget(self.export_excel_button)

        self.import_excel_button = QPushButton(TRANSLATIONS["import_excel"])
        self.import_excel_button.setIcon(qta.icon('fa5s.file-import', color='#D32F2F'))
        self.import_excel_button.clicked.connect(self.import_from_file)
        button_layout.addWidget(self.import_excel_button)

        self.pdf_button = QPushButton(TRANSLATIONS["generate_pdf"])
        self.pdf_button.setIcon(qta.icon('fa5s.file-pdf', color='#FFC107'))
        self.pdf_button.clicked.connect(self.generate_pdf_report)
        button_layout.addWidget(self.pdf_button)

        self.tools_button = QPushButton(TRANSLATIONS["tools"])
        self.tools_button.setIcon(qta.icon('fa5s.tools', color='#D32F2F'))
        self.tools_button.clicked.connect(self.open_tools)
        button_layout.addWidget(self.tools_button)

        self.close_button = QPushButton(TRANSLATIONS["close_item"])
        self.close_button.setIcon(qta.icon('fa5s.times', color='#D32F2F'))
        self.close_button.clicked.connect(self.close_application)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def setup_archive_tab(self):
        if self.archive_tab.layout() is not None:
            while self.archive_tab.layout().count():
                child = self.archive_tab.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.archive_tab.setLayout(QVBoxLayout())

        layout = self.archive_tab.layout()

        self.archive_table = QTableWidget()
        all_headers = self.get_column_headers() + [TRANSLATIONS["last_updated"]]
        self.archive_table.setColumnCount(len(all_headers))
        self.archive_table.setHorizontalHeaderLabels(all_headers)
        self.archive_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.archive_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        layout.addWidget(self.archive_table)

        button_layout = QHBoxLayout()
        self.view_button = QPushButton(TRANSLATIONS["view_item"])
        self.view_button.setIcon(qta.icon('fa5s.eye', color='#D32F2F'))
        self.view_button.clicked.connect(self.view_archive_item)
        button_layout.addWidget(self.view_button)

        self.restore_button = QPushButton(TRANSLATIONS["restore_item"])
        self.restore_button.setIcon(qta.icon('fa5s.undo', color='#FFC107'))
        self.restore_button.clicked.connect(self.restore_archive_item)
        button_layout.addWidget(self.restore_button)

        self.delete_archive_button = QPushButton(TRANSLATIONS["delete_item"])
        self.delete_archive_button.setIcon(qta.icon('fa5s.trash', color='#D32F2F'))
        self.delete_archive_button.clicked.connect(self.delete_archive_item_with_confirmation)
        button_layout.addWidget(self.delete_archive_button)

        self.close_button_archive = QPushButton(TRANSLATIONS["close_item"])
        self.close_button_archive.setIcon(qta.icon('fa5s.times', color='#D32F2F'))
        self.close_button_archive.clicked.connect(self.close_application)
        button_layout.addWidget(self.close_button_archive)

        layout.addLayout(button_layout)

    def setup_settings_tab(self):
        if self.settings_tab.layout() is not None:
            while self.settings_tab.layout().count():
                child = self.settings_tab.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.settings_tab.setLayout(QVBoxLayout())

        layout = self.settings_tab.layout()

        general_group = QGroupBox("Genel Ayarlar")
        general_layout = QFormLayout()

        self.font_size_spin = QSpinBox()
        self.font_size_spin.setRange(8, 24)
        self.font_size_spin.setValue(self.config["font_size"])
        self.font_size_spin.valueChanged.connect(self.change_font_size)
        general_layout.addRow(QLabel(TRANSLATIONS["font_size"]), self.font_size_spin)

        self.startup_group_combo = QComboBox()
        self.startup_group_combo.addItems([item["name"] for item in self.groups] + ["Son Kullanılan"])
        self.startup_group_combo.setCurrentText(self.config.get("startup_group", "Genel"))
        self.startup_group_combo.currentIndexChanged.connect(self.update_startup_group)
        general_layout.addRow(QLabel(TRANSLATIONS["startup_group"]), self.startup_group_combo)
        general_group.setLayout(general_layout)
        layout.addWidget(general_group)

        backup_group = QGroupBox("Yedekleme Ayarları")
        backup_layout = QFormLayout()
        self.backup_spin = QSpinBox()
        self.backup_spin.setRange(1, 1440)
        self.backup_spin.setValue(self.config["backup_frequency"])
        self.backup_spin.valueChanged.connect(self.update_backup_frequency)
        backup_layout.addRow(QLabel(TRANSLATIONS["backup_frequency"]), self.backup_spin)

        self.backup_path_edit = QLineEdit()
        self.backup_path_edit.setText(self.config["backup_path"])
        self.backup_path_edit.setReadOnly(True)
        self.backup_path_button = QPushButton("...")
        self.backup_path_button.clicked.connect(self.change_backup_path)
        path_layout = QHBoxLayout()
        path_layout.addWidget(self.backup_path_edit)
        path_layout.addWidget(self.backup_path_button)
        backup_layout.addRow(QLabel(TRANSLATIONS["backup_path"]), path_layout)

        self.retention_spin = QSpinBox()
        self.retention_spin.setRange(1, 365)
        self.retention_spin.setValue(self.config["backup_retention"])
        self.retention_spin.valueChanged.connect(self.update_backup_retention)
        backup_layout.addRow(QLabel(TRANSLATIONS["backup_retention"]), self.retention_spin)
        backup_group.setLayout(backup_layout)
        layout.addWidget(backup_group)

        data_group = QGroupBox("Veri Yönetimi Ayarları")
        data_layout = QFormLayout()
        self.default_group_combo = QComboBox()
        self.default_group_combo.addItems([item["name"] for item in self.groups])
        self.default_group_combo.setCurrentText(self.config["default_group"])
        self.default_group_combo.currentIndexChanged.connect(self.update_default_group)
        data_layout.addRow(QLabel(TRANSLATIONS["default_group"]), self.default_group_combo)

        self.autosave_spin = QSpinBox()
        self.autosave_spin.setRange(1, 60)
        self.autosave_spin.setValue(self.config["autosave_interval"])
        self.autosave_spin.valueChanged.connect(self.update_autosave_interval)
        data_layout.addRow(QLabel(TRANSLATIONS["autosave_interval"]), self.autosave_spin)

        self.export_format_combo = QComboBox()
        self.export_format_combo.addItems(["Excel (*.xlsx)", "CSV (*.csv)", "JSON (*.json)"])
        self.export_format_combo.setCurrentText(self.config["export_format"])
        self.export_format_combo.currentIndexChanged.connect(self.update_export_format)
        data_layout.addRow(QLabel(TRANSLATIONS["export_format"]), self.export_format_combo)
        data_group.setLayout(data_layout)
        layout.addWidget(data_group)

        reset_button = QPushButton(TRANSLATIONS["reset_settings"])
        reset_button.clicked.connect(self.reset_settings)
        layout.addWidget(reset_button)
        layout.addStretch()

    def setup_about_tab(self):
        if self.about_tab.layout() is not None:
            while self.about_tab.layout().count():
                child = self.about_tab.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        else:
            self.about_tab.setLayout(QVBoxLayout())

        layout = self.about_tab.layout()
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(20)

        CONTAINER_STYLE = "background: #f1faee; border-radius: 15px; padding: 20px; border: 1px solid #dfe6e9;"
        TITLE_STYLE = "color: #e63946; font-size: 20px; font-weight: bold; font-family: Arial, sans-serif;"
        TEXT_STYLE = "color: #457b9d; font-size: 14px; font-family: Arial, sans-serif;"
        SUBTEXT_STYLE = "color: #6c757d; font-size: 12px;"
        LINK_STYLE = "color: #1d3557; text-decoration: none;"
        LINK_HOVER = "color: #457b9d;"

        about_data = {
            "title": "Galatasaraylılar Yurdu\nEnvanter Kayıt Sistemi",
            "version": "1.0.0",
            "update_date": datetime.now().strftime("%d.%m.%Y"),
            "description": TRANSLATIONS.get("about_description", "Bu uygulama, envanter yönetimini kolaylaştırmak için tasarlanmıştır."),
            "contact": {
                "address": "Florya, Şenlikköy Mh. Orman Sk. No:39/1 Florya Bakırköy/İstanbul",
                "email": "bilgi@gsyardimlasmavakfi.org",
                "phone": "(0212) 574 52 55"
            },
            "developer": {
                "name": "Mustafa AKBAL",
                "email": "mstf.akbal@gmail.com",
                "phone": "+905447485959",
                "social": {
                    "GitHub": "https://github.com/chawresh",
                    "Instagram": "https://instagram.com/mstf.akbal"
                }
            },
            "copyright": TRANSLATIONS.get("about_copyright", "© 2025 Mustafa AKBAL. Tüm hakları saklıdır.")
        }

        container = QWidget()
        container.setStyleSheet(CONTAINER_STYLE)
        container.setFixedWidth(500)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)

        def generate_html(data):
            logo_html = f'<img src="{LOGO_FILE}" width="100" height="100" style="border-radius: 50%; border: 2px solid #e63946;">' if os.path.exists(LOGO_FILE) else '<p style="{TEXT_STYLE} text-align: center;">Logo bulunamadı</p>'
            social_links = "".join(
                f'<a href="{url}" style="{LINK_STYLE}" onmouseover="this.style.color=\'{LINK_HOVER}\';" onmouseout="this.style.color=\'#1d3557\';">{name}</a>' + (" " if i < len(data["developer"]["social"]) - 1 else "")
                for i, (name, url) in enumerate(data["developer"]["social"].items())
            )
            about_html = f"""
            <html>
            <body style="{TEXT_STYLE}">
                <div style="text-align: center; margin-bottom: 20px;">{logo_html}</div>
                <h1 style="{TITLE_STYLE} text-align: center; margin: 0;">{data["title"]}</h1>
                <p style="{SUBTEXT_STYLE} text-align: center; margin: 10px 0;">Sürüm: {data["version"]} • Güncelleme: {data["update_date"]}</p>
                <p style="{TEXT_STYLE} text-align: center; margin: 15px 0; line-height: 1.5;">{data["description"]}</p>
                <p style="{TEXT_STYLE} text-align: center; margin: 15px 0; line-height: 1.5;">
                    <b>Adres:</b> {data["contact"]["address"]}<br>
                    <b>E-posta:</b> <a href="mailto:{data["contact"]["email"]}" style="{LINK_STYLE}" onmouseover="this.style.color='{LINK_HOVER}';" onmouseout="this.style.color='#1d3557';">{data["contact"]["email"]}</a><br>
                    <b>Telefon:</b> {data["contact"]["phone"]}
                </p>
                <p style="{TEXT_STYLE} text-align: center; margin: 15px 0; line-height: 1.5;">
                    <b>Geliştirici:</b> {data["developer"]["name"]}<br>
                    <b>E-posta:</b> <a href="mailto:{data["developer"]["email"]}" style="{LINK_STYLE}" onmouseover="this.style.color='{LINK_HOVER}';" onmouseout="this.style.color='#1d3557';">{data["developer"]["email"]}</a><br>
                    <b>Telefon:</b> {data["developer"]["phone"]}<br>
                    <b>Sosyal:</b> {social_links}
                </p>
                <p style="{SUBTEXT_STYLE} text-align: center; font-style: italic; margin-top: 20px;">{data["copyright"]}</p>
            </body>
            </html>
            """
            return about_html

        about_label = QLabel()
        about_label.setText(generate_html(about_data))
        about_label.setWordWrap(True)
        about_label.setOpenExternalLinks(True)
        container_layout.addWidget(about_label)

        layout.addWidget(container)
        layout.addStretch()

    def load_config(self):
        default_config = {
            "backup_frequency": 5,
            "default_group": "Genel",
            "font_size": 12,
            "backup_path": os.path.join(FILES_DIR, "backups"),
            "backup_retention": 30,
            "autosave_interval": 5,
            "export_format": "Excel (*.xlsx)",
            "startup_group": "Genel"
        }
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                self.config = {**default_config, **json.load(f)}
        else:
            self.config = default_config.copy()

    def save_config(self):
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, ensure_ascii=False, indent=4)

    def change_font_size(self, size):
        font = QFont(self.default_font, size)
        QApplication.setFont(font)
        self.config["font_size"] = size
        self.save_config()

    def update_startup_group(self):
        self.config["startup_group"] = self.startup_group_combo.currentText()
        if self.config["startup_group"] != "Son Kullanılan":
            self.group_combo.setCurrentText(self.config["startup_group"])
        self.save_config()

    def change_backup_path(self):
        path = QFileDialog.getExistingDirectory(self, TRANSLATIONS["backup_path"], self.backup_path_edit.text())
        if path:
            self.backup_path_edit.setText(path)
            self.config["backup_path"] = path
            self.save_config()

    def update_backup_frequency(self):
        self.config["backup_frequency"] = self.backup_spin.value()
        self.backup_timer.stop()
        self.backup_timer.start(self.config["backup_frequency"] * 60000)
        self.save_config()

    def update_backup_retention(self):
        self.config["backup_retention"] = self.retention_spin.value()
        backup_dir = self.config["backup_path"]
        now = time.time()
        cutoff = now - (self.config["backup_retention"] * 86400)
        for backup_file in glob.glob(os.path.join(backup_dir, "inventory_backup_*.db")):
            if os.path.getctime(backup_file) < cutoff:
                os.remove(backup_file)
        self.save_config()

    def update_default_group(self):
        self.config["default_group"] = self.default_group_combo.currentText()
        self.group_combo.setCurrentText(self.config["default_group"])
        self.save_config()

    def update_autosave_interval(self):
        self.config["autosave_interval"] = self.autosave_spin.value()
        self.autosave_timer.stop()
        self.autosave_timer.start(self.config["autosave_interval"] * 60000)
        self.save_config()

    def update_export_format(self):
        self.config["export_format"] = self.export_format_combo.currentText()
        self.save_config()

    def reset_settings(self):
        if QMessageBox.question(self, "Ayarları Sıfırla",
                                "Tüm ayarları sıfırlamak istediğinizden emin misiniz?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            self.config = {
                "backup_frequency": 5,
                "default_group": "Genel",
                "font_size": 12,
                "backup_path": os.path.join(FILES_DIR, "backups"),
                "backup_retention": 30,
                "autosave_interval": 5,
                "export_format": "Excel (*.xlsx)",
                "startup_group": "Genel"
            }
            self.backup_spin.setValue(5)
            self.default_group_combo.setCurrentText(self.config["default_group"])
            self.font_size_spin.setValue(12)
            self.backup_path_edit.setText(os.path.join(FILES_DIR, "backups"))
            self.retention_spin.setValue(30)
            self.autosave_spin.setValue(5)
            self.export_format_combo.setCurrentText("Excel (*.xlsx)")
            self.startup_group_combo.setCurrentText(self.config["startup_group"])
            self.change_font_size(self.config["font_size"])
            self.save_config()
            self.setup_inventory_tab()
            self.setup_archive_tab()
            self.setup_settings_tab()
            self.setup_about_tab()
            QMessageBox.information(self, "Ayarlar Sıfırlandı",
                                    "Tüm ayarlar varsayılan değerlerine sıfırlandı.")

    def load_data_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, data, timestamp FROM inventory")
        rows = cursor.fetchall()
        headers = self.get_column_headers()
        self.table.setRowCount(len(rows))
        self.table.setColumnCount(len(headers) + 1)
        self.table.setHorizontalHeaderLabels(headers + [TRANSLATIONS["last_updated"]])
        for row_idx, (row_id, row_data, timestamp) in enumerate(rows):
            data = json.loads(row_data)
            if len(data) < len(headers):
                data.extend([""] * (len(headers) - len(data)))
            for col, value in enumerate(data):
                self.table.setItem(row_idx, col, QTableWidgetItem(str(value)))
            self.table.setItem(row_idx, len(headers), QTableWidgetItem(timestamp))
            if self.table.item(row_idx, 0):
                self.table.item(row_idx, 0).setData(Qt.UserRole, row_id)

    def load_archive_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, data, timestamp FROM archive")
        rows = cursor.fetchall()
        headers = self.get_column_headers()
        self.archive_table.setRowCount(len(rows))
        self.archive_table.setColumnCount(len(headers) + 1)
        self.archive_table.setHorizontalHeaderLabels(headers + [TRANSLATIONS["last_updated"]])
        for row_idx, (row_id, row_data, timestamp) in enumerate(rows):
            data = json.loads(row_data)
            if len(data) < len(headers):
                data.extend([""] * (len(headers) - len(data)))
            for col, value in enumerate(data):
                self.archive_table.setItem(row_idx, col, QTableWidgetItem(str(value)))
            self.archive_table.setItem(row_idx, len(headers), QTableWidgetItem(timestamp))
            if self.archive_table.item(row_idx, 0):
                self.archive_table.item(row_idx, 0).setData(Qt.UserRole, row_id)

    def add_item(self):
        headers = self.get_column_headers()
        data = []
        for header in headers:
            if header in self.card_entries:
                if header == TRANSLATIONS["purchase_date"]:
                    if f"{header}_check" in self.card_entries and self.card_entries[f"{header}_check"].isChecked():
                        value = TRANSLATIONS["unknown"]
                    else:
                        value = self.card_entries[header].date().toString("dd.MM.yyyy")
                else:
                    value = self.get_widget_value(self.card_entries[header])
            elif header in self.invoice_entries:
                value = self.get_widget_value(self.invoice_entries[header])
            elif header in self.service_entries:
                if header == TRANSLATIONS["warranty_period"]:
                    if f"{header}_check" in self.service_entries and self.service_entries[f"{header}_check"].isChecked():
                        value = TRANSLATIONS["unknown"]
                    else:
                        value = self.service_entries[header].date().toString("dd.MM.yyyy")
                else:
                    value = self.get_widget_value(self.service_entries[header])
            else:
                value = ""
            data.append(value)

        group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
        item_name_idx = headers.index(TRANSLATIONS["item_name"]) if TRANSLATIONS["item_name"] in headers else -1
        region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
        floor_idx = headers.index(TRANSLATIONS["floor"]) if TRANSLATIONS["floor"] in headers else -1
        code_idx = headers.index("Kod") if "Kod" in headers else -1

        if group_name_idx == -1 or item_name_idx == -1 or not data[group_name_idx] or not data[item_name_idx]:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_all_fields"])
            return

        group_name = data[group_name_idx]
        region_name = data[region_idx] if region_idx != -1 and region_idx < len(data) else ""
        floor_name = data[floor_idx] if floor_idx != -1 and floor_idx < len(data) else ""
        inventory_code = self.generate_inventory_code(group_name, region_name, floor_name)

        if code_idx != -1:
            data[code_idx] = inventory_code
        else:
            cursor = self.conn.cursor()
            cursor.execute("SELECT MAX(column_order) FROM metadata")
            max_order = cursor.fetchone()[0] or 0
            cursor.execute("INSERT INTO metadata (column_name, column_order, section) VALUES (?, ?, ?)",
                           ("Kod", 0, TRANSLATIONS["card_info"]))
            self.conn.commit()
            headers.insert(0, "Kod")
            data.insert(0, inventory_code)
            self.setup_inventory_tab()

        if group_name_idx != -1:
            data[group_name_idx] = group_name

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(data), timestamp))
        self.conn.commit()
        self.load_data_from_db()
        QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_added"] + f"\nKod: {inventory_code}")
        for entry in list(self.card_entries.values()) + list(self.invoice_entries.values()) + list(self.service_entries.values()):
            if isinstance(entry, QLineEdit):
                entry.clear()
            elif isinstance(entry, QDateEdit):
                entry.setDate(datetime.now().date())
            elif isinstance(entry, QTextEdit):
                entry.clear()
            elif isinstance(entry, QCheckBox):
                entry.setChecked(False)

    def open_edit_dialog(self, item=None):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        headers = self.get_column_headers()
        row_data = [self.table.item(selected, col).text() if self.table.item(selected, col) else "" for col in range(len(headers))]
        dialog = EditDialog(self, row_data, headers)
        if dialog.exec_():
            updated_data = dialog.get_data()
            row_id = self.table.item(selected, 0).data(Qt.UserRole)
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
            region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
            floor_idx = headers.index(TRANSLATIONS["floor"]) if TRANSLATIONS["floor"] in headers else -1
            code_idx = headers.index("Kod") if "Kod" in headers else -1

            if group_name_idx != -1 and region_idx != -1 and floor_idx != -1:
                group_name = updated_data[group_name_idx]
                region_name = updated_data[region_idx]
                floor_name = updated_data[floor_idx]
                new_code = self.generate_inventory_code(group_name, region_name, floor_name)
                if code_idx != -1:
                    updated_data[code_idx] = new_code

            cursor = self.conn.cursor()
            cursor.execute("UPDATE inventory SET data = ?, timestamp = ? WHERE id = ?", (json.dumps(updated_data), timestamp, row_id))
            self.conn.commit()
            self.load_data_from_db()
            QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_updated"])

    def archive_item_with_confirmation(self):
        selected = self.table.currentRow()
        if selected >= 0:
            if QMessageBox.question(self, "Onay", TRANSLATIONS["confirm_archive"],
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                row_id = self.table.item(selected, 0).data(Qt.UserRole)
                cursor = self.conn.cursor()
                cursor.execute("SELECT data, timestamp FROM inventory WHERE id = ?", (row_id,))
                data, timestamp = cursor.fetchone()
                cursor.execute("INSERT INTO archive (data, timestamp) VALUES (?, ?)", (data, timestamp))
                cursor.execute("DELETE FROM inventory WHERE id = ?", (row_id,))
                self.conn.commit()
                self.load_data_from_db()
                self.load_archive_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_archived"])
        else:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])

    def delete_item_with_double_confirmation(self):
        selected = self.table.currentRow()
        if selected >= 0:
            if QMessageBox.question(self, "Onay", TRANSLATIONS["confirm_delete"],
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                if QMessageBox.question(self, "Son Onay", TRANSLATIONS["confirm_delete_final"],
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    row_id = self.table.item(selected, 0).data(Qt.UserRole)
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM inventory WHERE id = ?", (row_id,))
                    self.conn.commit()
                    self.load_data_from_db()
                    QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_deleted"])
        else:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])

    def delete_archive_item_with_confirmation(self):
        selected = self.archive_table.currentRow()
        if selected >= 0:
            if QMessageBox.question(self, "Onay", TRANSLATIONS["confirm_delete"],
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                if QMessageBox.question(self, "Son Onay", TRANSLATIONS["confirm_delete_final"],
                                        QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                    row_id = self.archive_table.item(selected, 0).data(Qt.UserRole)
                    cursor = self.conn.cursor()
                    cursor.execute("DELETE FROM archive WHERE id = ?", (row_id,))
                    self.conn.commit()
                    self.load_archive_from_db()
                    QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_deleted"])
        else:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])

    def duplicate_item(self):
        selected = self.table.currentRow()
        if selected >= 0:
            headers = self.get_column_headers()
            data = [self.table.item(selected, col).text() if self.table.item(selected, col) else "" for col in range(len(headers))]
            group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
            region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
            floor_idx = headers.index(TRANSLATIONS["floor"]) if TRANSLATIONS["floor"] in headers else -1
            code_idx = headers.index("Kod") if "Kod" in headers else -1

            if group_name_idx != -1 and region_idx != -1 and floor_idx != -1 and code_idx != -1:
                group_name = data[group_name_idx]
                region_name = data[region_idx]
                floor_name = data[floor_idx]
                data[code_idx] = self.generate_inventory_code(group_name, region_name, floor_name)

            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(data), timestamp))
            self.conn.commit()
            self.load_data_from_db()
            QMessageBox.information(self, "Başarılı", "Envanter çoğaltıldı.")
        else:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])

    def show_details(self):
        selected = self.table.currentRow()
        if selected < 0:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return

        try:
            headers = self.get_column_headers()
            if not headers:
                QMessageBox.warning(self, "Hata", "Sütun başlıkları alınamadı!")
                return

            data = []
            for col in range(len(headers)):
                item = self.table.item(selected, col)
                data.append(item.text() if item else "Bilgi Yok")

            dialog = QDialog(self)
            dialog.setWindowTitle(TRANSLATIONS["details_title"])
            dialog.setMinimumSize(800, 600)
            layout = QVBoxLayout(dialog)

            tabs = QTabWidget()
            card_tab = QWidget()
            invoice_tab = QWidget()
            service_tab = QWidget()

            card_layout = QFormLayout(card_tab)
            invoice_layout = QFormLayout(invoice_tab)
            service_layout = QFormLayout(service_tab)

            cursor = self.conn.cursor()
            cursor.execute("SELECT column_name, section FROM metadata ORDER BY column_order")
            metadata = cursor.fetchall()
            if not metadata:
                logging.warning("Metadata tablosu boş, varsayılan bölüm kullanılıyor.")
                metadata = [(header, TRANSLATIONS["card_info"]) for header in headers]

            card_count = 0
            invoice_count = 0
            service_count = 0

            for header, value in zip(headers, data):
                section = next((m[1] for m in metadata if m[0] == header), TRANSLATIONS["card_info"])
                label = QLabel(f"{header}:")
                label.setStyleSheet("font-weight: bold;")
                value_label = QLabel(value)
                value_label.setWordWrap(True)
                value_label.setStyleSheet("margin-left: 10px;")

                if section == TRANSLATIONS["card_info"]:
                    card_layout.addRow(label, value_label)
                    card_count += 1
                elif section == TRANSLATIONS["invoice_info"]:
                    invoice_layout.addRow(label, value_label)
                    invoice_count += 1
                elif section == TRANSLATIONS["service_info"]:
                    service_layout.addRow(label, value_label)
                    service_count += 1

            tabs.addTab(card_tab, f"{TRANSLATIONS['card_info']} ({card_count})")
            tabs.addTab(invoice_tab, f"{TRANSLATIONS['invoice_info']} ({invoice_count})")
            tabs.addTab(service_tab, f"{TRANSLATIONS['service_info']} ({service_count})")
            layout.addWidget(tabs)

            code_idx = headers.index("Kod") if "Kod" in headers else -1
            if code_idx != -1 and code_idx < len(data):
                code = data[code_idx]
                decoded_info = self.decode_inventory_code(code)
                code_label = QLabel(f"Kod Çözümleme: {decoded_info}")
                code_label.setStyleSheet("font-weight: bold; color: #D32F2F; margin-top: 10px;")
                layout.addWidget(code_label)

            button_layout = QHBoxLayout()
            copy_button = QPushButton("Detayları Kopyala")
            copy_button.setIcon(qta.icon('fa5s.copy', color='#FFC107'))
            copy_button.clicked.connect(lambda: QApplication.clipboard().setText(
                "\n".join([f"{header}: {value}" for header, value in zip(headers, data)])
            ))
            button_layout.addWidget(copy_button)

            pdf_button = QPushButton("PDF Olarak Kaydet")
            pdf_button.setIcon(qta.icon('fa5s.file-pdf', color='#FFC107'))
            pdf_button.clicked.connect(lambda: self.save_details_as_pdf(headers, data))
            button_layout.addWidget(pdf_button)

            close_button = QPushButton(TRANSLATIONS["close_item"])
            close_button.setIcon(qta.icon('fa5s.times', color='#D32F2F'))
            close_button.clicked.connect(dialog.accept)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Detaylar gösterilirken hata oluştu: {str(e)}")
            logging.error(f"show_details hatası: {str(e)}")

    def save_details_as_pdf(self, headers, data):
        file_name, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "", "PDF (*.pdf)")
        if file_name:
            try:
                doc = SimpleDocTemplate(file_name, pagesize=A4)
                elements = []
                styles = getSampleStyleSheet()
                title_style = styles['Heading1']
                title_style.alignment = 1
                title_style.fontName = self.default_font

                title = Paragraph(TRANSLATIONS["details_title"], title_style)
                elements.append(title)
                elements.append(Spacer(1, 0.5 * cm))

                if os.path.exists(LOGO_FILE):
                    logo = Image(LOGO_FILE, width=2 * cm, height=2 * cm)
                    elements.append(logo)
                    elements.append(Spacer(1, 0.5 * cm))

                table_data = [["Alan", "Değer"]]
                for header, value in zip(headers, data):
                    table_data.append([header, value])

                table = Table(table_data)
                table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                    ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                    ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ]))
                elements.append(table)

                doc.build(elements)
                QMessageBox.information(self, "Başarılı", "Detaylar PDF olarak kaydedildi!")
                logging.info(f"Detaylar PDF olarak {file_name} dosyasına kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturma başarısız: {str(e)}")
                logging.error(f"PDF oluşturma hatası: {str(e)}")

    def view_archive_item(self):
        selected = self.archive_table.currentRow()
        if selected >= 0:
            headers = self.get_column_headers()
            data = [self.archive_table.item(selected, col).text() if self.archive_table.item(selected, col) else "" for col in range(len(headers))]
            dialog = QDialog(self)
            dialog.setWindowTitle(TRANSLATIONS["details_title"])
            layout = QVBoxLayout(dialog)
            detail_table = QTableWidget(len(headers), 2)
            detail_table.setHorizontalHeaderLabels(["Alan", "Değer"])
            detail_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for row, (header, value) in enumerate(zip(headers, data)):
                detail_table.setItem(row, 0, QTableWidgetItem(header))
                detail_table.setItem(row, 1, QTableWidgetItem(value))
            layout.addWidget(detail_table)
            close_button = QPushButton(TRANSLATIONS["close_item"])
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])

    def restore_archive_item(self):
        selected = self.archive_table.currentRow()
        if selected >= 0:
            headers = self.get_column_headers()
            row_data = [self.archive_table.item(selected, col).text() if self.archive_table.item(selected, col) else "" for col in range(len(headers))]
            dialog = EditDialog(self, row_data, headers)
            if dialog.exec_():
                updated_data = dialog.get_data()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                row_id = self.archive_table.item(selected, 0).data(Qt.UserRole)
                cursor = self.conn.cursor()
                cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(updated_data), timestamp))
                cursor.execute("DELETE FROM archive WHERE id = ?", (row_id,))
                self.conn.commit()
                self.load_data_from_db()
                self.load_archive_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_restored"])
        else:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])

    def export_to_file(self):
        headers = self.get_column_headers()
        data = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(len(headers))]
            data.append(row_data)

        if not data:
            QMessageBox.warning(self, "Hata", "Dışa aktarılacak veri yok!")
            return

        file_format = self.config["export_format"]
        file_name, _ = QFileDialog.getSaveFileName(self, "Dosyayı Kaydet", "", file_format)
        if file_name:
            try:
                df = pd.DataFrame(data, columns=headers)
                if file_format == "Excel (*.xlsx)":
                    df.to_excel(file_name, index=False)
                elif file_format == "CSV (*.csv)":
                    df.to_csv(file_name, index=False)
                elif file_format == "JSON (*.json)":
                    df.to_json(file_name, orient="records", force_ascii=False)
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["excel_exported"])
                logging.info(f"Veriler {file_name} dosyasına {file_format} formatında aktarıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {str(e)}")
                logging.error(f"Dışa aktarma hatası: {str(e)}")

    def import_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Excel (*.xlsx);;CSV (*.csv);;JSON (*.json)")
        if file_name:
            try:
                if file_name.endswith(".xlsx"):
                    df = pd.read_excel(file_name)
                elif file_name.endswith(".csv"):
                    df = pd.read_csv(file_name)
                elif file_name.endswith(".json"):
                    df = pd.read_json(file_name)
                else:
                    QMessageBox.warning(self, "Hata", "Desteklenmeyen dosya formatı!")
                    return

                headers = self.get_column_headers()
                cursor = self.conn.cursor()

                choice = QMessageBox.question(self, "Veri İçe Aktarma",
                                              "Mevcut verilerin üzerine yazmak mı istiyorsunuz? (Hayır seçilirse ekleme yapılır)",
                                              QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                if choice == QMessageBox.Cancel:
                    return
                elif choice == QMessageBox.Yes:
                    cursor.execute("DELETE FROM inventory")

                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                for _, row in df.iterrows():
                    data = [str(row.get(header, "")) for header in headers]
                    cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(data), timestamp))
                self.conn.commit()
                self.load_data_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["excel_imported"])
                logging.info(f"Veriler {file_name} dosyasından içe aktarıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"İçe aktarma başarısız: {str(e)}")
                logging.error(f"İçe aktarma hatası: {str(e)}")

    def generate_pdf_report(self):
        headers = self.get_column_headers()
        dialog = ColumnSelectionDialog(headers, self)
        if dialog.exec_():
            selected_columns = dialog.get_selected_columns()
            if not selected_columns:
                QMessageBox.warning(self, "Hata", "En az bir sütun seçmelisiniz!")
                return

            file_name, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "", "PDF (*.pdf)")
            if file_name:
                try:
                    doc = SimpleDocTemplate(file_name, pagesize=landscape(A4))
                    elements = []
                    styles = getSampleStyleSheet()
                    title_style = styles['Heading1']
                    title_style.alignment = 1
                    title_style.fontName = self.default_font

                    title = Paragraph(TRANSLATIONS["title"], title_style)
                    elements.append(title)
                    elements.append(Spacer(1, 0.5 * cm))

                    if os.path.exists(LOGO_FILE):
                        logo = Image(LOGO_FILE, width=2 * cm, height=2 * cm)
                        elements.append(logo)
                        elements.append(Spacer(1, 0.5 * cm))

                    data = []
                    table_headers = [header for header in headers if header in selected_columns]
                    data.append(table_headers)

                    for row in range(self.table.rowCount()):
                        row_data = [self.table.item(row, headers.index(header)).text() if self.table.item(row, headers.index(header)) else ""
                                    for header in table_headers]
                        data.append(row_data)

                    table = Table(data)
                    table.setStyle(TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                        ('FONTSIZE', (0, 0), (-1, -1), 10),
                        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 1, colors.black)
                    ]))
                    elements.append(table)

                    doc.build(elements)
                    QMessageBox.information(self, "Başarılı", TRANSLATIONS["pdf_generated"])
                    logging.info(f"PDF raporu {file_name} olarak oluşturuldu.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"PDF oluşturma başarısız: {str(e)}")
                    logging.error(f"PDF oluşturma hatası: {str(e)}")

    def open_tools(self):
        menu = QMenu(self)
        menu.addAction(qta.icon('fa5s.chart-bar', color='#D32F2F'), TRANSLATIONS["data_analysis"],
                       self.data_analysis)
        backup_menu = menu.addMenu(qta.icon('fa5s.save', color='#D32F2F'), TRANSLATIONS["backup_operations"])
        backup_menu.addAction(qta.icon('fa5s.download', color='#FFC107'), TRANSLATIONS["manual_backup"],
                              self.manual_backup)
        menu.addSeparator()

        param_menu = menu.addMenu(qta.icon('fa5s.cogs', color='#D32F2F'), TRANSLATIONS["param_management"])
        param_menu.addAction(qta.icon('fa5s.plus', color='#FFC107'), TRANSLATIONS["add_parameter"],
                             self.add_parameter)
        param_menu.addAction(qta.icon('fa5s.trash', color='#D32F2F'), TRANSLATIONS["delete_parameter"],
                             self.delete_parameter)
        param_menu.addAction(qta.icon('fa5s.edit', color='#FFC107'), TRANSLATIONS["edit_parameter"],
                             self.edit_parameter)
        param_menu.addSeparator()
        param_menu.addAction(qta.icon('fa5s.users', color='#FFC107'), TRANSLATIONS["edit_groups"],
                             lambda: self.edit_combobox(TRANSLATIONS["edit_groups"], self.groups, GROUPS_FILE))
        param_menu.addAction(qta.icon('fa5s.user', color='#FFC107'), TRANSLATIONS["edit_users"],
                             lambda: self.edit_combobox(TRANSLATIONS["edit_users"], self.users, USERS_FILE))
        param_menu.addAction(qta.icon('fa5s.map', color='#FFC107'), TRANSLATIONS["edit_regions"],
                             lambda: self.edit_combobox(TRANSLATIONS["edit_regions"], self.regions, REGIONS_FILE))
        param_menu.addAction(qta.icon('fa5s.building', color='#FFC107'), TRANSLATIONS["edit_floors"],
                             lambda: self.edit_combobox(TRANSLATIONS["edit_floors"], self.floors, FLOORS_FILE))

        menu.addAction(qta.icon('fa5s.search', color='#D32F2F'), "Kod Çözümle",
                       self.decode_inventory_code_dialog)

        menu.exec_(self.tools_button.mapToGlobal(self.tools_button.rect().bottomLeft()))

    def decode_inventory_code_dialog(self):
        while True:
            code, ok = QInputDialog.getText(self, "Kod Çözümle", "Çözümlenecek envanter kodunu girin (örneğin, MOB-SAL-KE1):")
            if not ok:
                return
            if not code or "-" not in code or len(code.split("-")) != 3:
                QMessageBox.warning(self, "Hata", "Geçersiz kod formatı! Kod, GRUP-BÖLGE-KAT formatında olmalıdır. Negatif katlar için KM formatı kullanılır (örneğin, KE1 = Kat -1). Tekrar deneyin.")
            else:
                break
        logging.info(f"Çözümlenmeye çalışılan kod: {code}")
        result = self.decode_inventory_code(code)
        QMessageBox.information(self, "Kod Çözümleme Sonucu", result)

    def data_analysis(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["analysis_title"])
        dialog.setMinimumSize(1000, 700)
        main_layout = QVBoxLayout(dialog)

        filter_group = QGroupBox("Filtreleme Seçenekleri")
        filter_layout = QHBoxLayout()

        group_label = QLabel("Grup:")
        self.group_filter_combo = QComboBox()
        self.group_filter_combo.addItem("Tümü")
        self.group_filter_combo.addItems([item["name"] for item in self.groups])
        filter_layout.addWidget(group_label)
        filter_layout.addWidget(self.group_filter_combo)

        region_label = QLabel("Bölge:")
        self.region_filter_combo = QComboBox()
        self.region_filter_combo.addItem("Tümü")
        self.region_filter_combo.addItems([item["name"] for item in self.regions])
        filter_layout.addWidget(region_label)
        filter_layout.addWidget(self.region_filter_combo)

        floor_label = QLabel("Kat:")
        self.floor_filter_combo = QComboBox()
        self.floor_filter_combo.addItem("Tümü")
        self.floor_filter_combo.addItems([item["name"] for item in self.floors])
        filter_layout.addWidget(floor_label)
        filter_layout.addWidget(self.floor_filter_combo)

        apply_filter_button = QPushButton("Filtre Uygula")
        apply_filter_button.setIcon(qta.icon('fa5s.filter', color='#D32F2F'))
        apply_filter_button.clicked.connect(lambda: self.update_analysis(dialog))
        filter_layout.addWidget(apply_filter_button)

        filter_group.setLayout(filter_layout)
        main_layout.addWidget(filter_group)

        self.analysis_tabs = QTabWidget()
        main_layout.addWidget(self.analysis_tabs)

        self.update_analysis(dialog)

        button_layout = QHBoxLayout()
        export_button = QPushButton("Analizi Dışa Aktar")
        export_button.setIcon(qta.icon('fa5s.file-export', color='#FFC107'))
        export_button.clicked.connect(lambda: self.export_analysis(dialog))
        button_layout.addWidget(export_button)

        close_button = QPushButton(TRANSLATIONS["close_item"])
        close_button.setIcon(qta.icon('fa5s.times', color='#D32F2F'))
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)

        main_layout.addLayout(button_layout)
        dialog.exec_()

    def update_analysis(self, dialog):
        self.analysis_tabs.clear()

        cursor = self.conn.cursor()

        where_clauses = []
        params = []
        if self.group_filter_combo.currentText() != "Tümü":
            where_clauses.append("json_extract(data, '$[1]') = ?")
            params.append(self.group_filter_combo.currentText())
        if self.region_filter_combo.currentText() != "Tümü":
            where_clauses.append("json_extract(data, '$[8]') = ?")
            params.append(self.region_filter_combo.currentText())
        if self.floor_filter_combo.currentText() != "Tümü":
            where_clauses.append("json_extract(data, '$[9]') = ?")
            params.append(self.floor_filter_combo.currentText())

        where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

        cursor.execute(f"SELECT COUNT(*) FROM inventory{where_sql}", params)
        total_records = cursor.fetchone()[0]

        cursor.execute(f"SELECT json_extract(data, '$[1]'), COUNT(*) FROM inventory{where_sql} GROUP BY json_extract(data, '$[1]')", params)
        group_dist = cursor.fetchall()
        group_names = [row[0] for row in group_dist]
        group_counts = [row[1] for row in group_dist]

        cursor.execute(f"SELECT json_extract(data, '$[8]'), COUNT(*) FROM inventory{where_sql} GROUP BY json_extract(data, '$[8]')", params)
        region_dist = cursor.fetchall()
        region_names = [row[0] for row in region_dist]
        region_counts = [row[1] for row in region_dist]

        cursor.execute(f"SELECT json_extract(data, '$[9]'), COUNT(*) FROM inventory{where_sql} GROUP BY json_extract(data, '$[9]')", params)
        floor_dist = cursor.fetchall()
        floor_names = [row[0] for row in floor_dist]
        floor_counts = [row[1] for row in floor_dist]

        cursor.execute(f"SELECT strftime('%Y-%m', timestamp), COUNT(*) FROM inventory{where_sql} GROUP BY strftime('%Y-%m', timestamp)", params)
        time_dist = cursor.fetchall()
        time_periods = [row[0] for row in time_dist]
        time_counts = [row[1] for row in time_dist]

        cursor.execute(f"SELECT AVG(CAST(json_extract(data, '$[4]') AS REAL)) FROM inventory{where_sql} WHERE json_extract(data, '$[4]') != ''", params)
        avg_cost = cursor.fetchone()[0]
        avg_cost = round(avg_cost, 2) if avg_cost else 0.0

        cursor.execute(f"SELECT json_extract(data, '$[6]') FROM inventory{where_sql} WHERE json_extract(data, '$[6]') != ''", params)
        warranty_dates = cursor.fetchall()
        current_date = datetime.now()
        active_warranties = sum(1 for date_str in warranty_dates if date_str[0] and date_str[0] != TRANSLATIONS["unknown"] and datetime.strptime(date_str[0], "%d.%m.%Y") > current_date)
        expired_warranties = len(warranty_dates) - active_warranties

        overview_tab = QWidget()
        overview_layout = QVBoxLayout(overview_tab)
        overview_text = QTextEdit()
        overview_text.setReadOnly(True)
        overview_text.setText(
            f"{TRANSLATIONS['total_records'].format(total_records)}\n\n"
            f"{TRANSLATIONS['group_distribution']}\n" + "\n".join([f"{name}: {count}" for name, count in group_dist]) + "\n\n"
            f"Ortalama Alış Bedeli: {avg_cost} TL\n\n"
            f"Garanti Durumu:\n- Aktif Garantili Ürünler: {active_warranties}\n- Garantisi Bitmiş Ürünler: {expired_warranties}"
        )
        overview_layout.addWidget(QLabel("Genel Bakış"))
        overview_layout.addWidget(overview_text)
        self.analysis_tabs.addTab(overview_tab, "Genel Bakış")

        group_tab = QWidget()
        group_layout = QVBoxLayout(group_tab)
        fig, ax = plt.subplots(figsize=(8, 4))
        bars = ax.bar(group_names, group_counts, color='#D32F2F')
        ax.set_title("Grup Dağılımı")
        ax.set_xlabel("Gruplar")
        ax.set_ylabel("Ürün Sayısı")
        plt.xticks(rotation=45, ha="right")
        fig.tight_layout()
        canvas = FigureCanvas(fig)
        group_layout.addWidget(QLabel("Grup Dağılım Grafiği"))
        group_layout.addWidget(canvas)
        try:
            cursor_mpl = mplcursors.cursor(bars, hover=True)
            cursor_mpl.connect("add", lambda sel: sel.annotation.set_text(f"{group_names[sel.target.index]}: {group_counts[sel.target.index]}"))
        except ImportError:
            pass
        self.analysis_tabs.addTab(group_tab, "Grup Dağılımı")

        region_tab = QWidget()
        region_layout = QVBoxLayout(region_tab)
        fig2, ax2 = plt.subplots(figsize=(8, 4))
        bars2 = ax2.bar(region_names, region_counts, color='#FFC107')
        ax2.set_title("Bölge Dağılımı")
        ax2.set_xlabel("Bölgeler")
        ax2.set_ylabel("Ürün Sayısı")
        plt.xticks(rotation=45, ha="right")
        fig2.tight_layout()
        canvas2 = FigureCanvas(fig2)
        region_layout.addWidget(QLabel("Bölge Dağılım Grafiği"))
        region_layout.addWidget(canvas2)
        try:
            cursor2 = mplcursors.cursor(bars2, hover=True)
            cursor2.connect("add", lambda sel: sel.annotation.set_text(f"{region_names[sel.target.index]}: {region_counts[sel.target.index]}"))
        except ImportError:
            pass
        self.analysis_tabs.addTab(region_tab, "Bölge Dağılımı")

        floor_tab = QWidget()
        floor_layout = QVBoxLayout(floor_tab)
        fig3, ax3 = plt.subplots(figsize=(8, 4))
        bars3 = ax3.bar(floor_names, floor_counts, color='#457b9d')
        ax3.set_title("Kat Dağılımı")
        ax3.set_xlabel("Katlar")
        ax3.set_ylabel("Ürün Sayısı")
        plt.xticks(rotation=45, ha="right")
        fig3.tight_layout()
        canvas3 = FigureCanvas(fig3)
        floor_layout.addWidget(QLabel("Kat Dağılım Grafiği"))
        floor_layout.addWidget(canvas3)
        try:
            cursor3 = mplcursors.cursor(bars3, hover=True)
            cursor3.connect("add", lambda sel: sel.annotation.set_text(f"{floor_names[sel.target.index]}: {floor_counts[sel.target.index]}"))
        except ImportError:
            pass
        self.analysis_tabs.addTab(floor_tab, "Kat Dağılımı")

        time_tab = QWidget()
        time_layout = QVBoxLayout(time_tab)
        fig4, ax4 = plt.subplots(figsize=(8, 4))
        ax4.plot(time_periods, time_counts, marker='o', color='#1d3557')
        ax4.set_title("Zaman Bazlı Ürün Eklenmesi")
        ax4.set_xlabel("Ay (YYYY-MM)")
        ax4.set_ylabel("Ürün Sayısı")
        plt.xticks(rotation=45, ha="right")
        fig4.tight_layout()
        canvas4 = FigureCanvas(fig4)
        time_layout.addWidget(QLabel("Zaman Bazlı Analiz"))
        time_layout.addWidget(canvas4)
        self.analysis_tabs.addTab(time_tab, "Zaman Analizi")

        detail_tab = QWidget()
        detail_layout = QVBoxLayout(detail_tab)
        detail_table = QTableWidget()
        headers = self.get_column_headers()
        cursor.execute(f"SELECT data FROM inventory{where_sql}", params)
        rows = cursor.fetchall()
        detail_table.setRowCount(len(rows))
        detail_table.setColumnCount(len(headers))
        detail_table.setHorizontalHeaderLabels(headers)
        for row_idx, row_data in enumerate(rows):
            data = json.loads(row_data[0])
            for col_idx, value in enumerate(data):
                if col_idx < len(headers):
                    detail_table.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
        detail_table.resizeColumnsToContents()
        detail_layout.addWidget(QLabel("Detaylı Veri Tablosu"))
        detail_layout.addWidget(detail_table)
        self.analysis_tabs.addTab(detail_tab, "Detaylı Veri")

    def export_analysis(self, dialog):
        export_dialog = QDialog(self)
        export_dialog.setWindowTitle("Dışa Aktarma Seçenekleri")
        export_layout = QVBoxLayout(export_dialog)

        export_overview = QCheckBox("Genel Bakış")
        export_overview.setChecked(True)
        export_groups = QCheckBox("Grup Dağılımı")
        export_groups.setChecked(True)
        export_regions = QCheckBox("Bölge Dağılımı")
        export_regions.setChecked(True)
        export_floors = QCheckBox("Kat Dağılımı")
        export_floors.setChecked(True)
        export_time = QCheckBox("Zaman Analizi")
        export_time.setChecked(True)
        export_details = QCheckBox("Detaylı Veri")
        export_details.setChecked(True)

        export_layout.addWidget(QLabel("Dışa aktarılacak bölümleri seçin:"))
        export_layout.addWidget(export_overview)
        export_layout.addWidget(export_groups)
        export_layout.addWidget(export_regions)
        export_layout.addWidget(export_floors)
        export_layout.addWidget(export_time)
        export_layout.addWidget(export_details)

        format_combo = QComboBox()
        format_combo.addItems(["Excel (*.xlsx)", "PDF (*.pdf)"])
        export_layout.addWidget(QLabel("Dışa Aktarma Formatı:"))
        export_layout.addWidget(format_combo)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(export_dialog.accept)
        button_box.rejected.connect(export_dialog.reject)
        export_layout.addWidget(button_box)

        if export_dialog.exec_():
            file_name, _ = QFileDialog.getSaveFileName(self, "Analizi Kaydet", "", format_combo.currentText())
            if file_name:
                try:
                    cursor = self.conn.cursor()
                    where_clauses = []
                    params = []
                    if self.group_filter_combo.currentText() != "Tümü":
                        where_clauses.append("json_extract(data, '$[1]') = ?")
                        params.append(self.group_filter_combo.currentText())
                    if self.region_filter_combo.currentText() != "Tümü":
                        where_clauses.append("json_extract(data, '$[8]') = ?")
                        params.append(self.region_filter_combo.currentText())
                    if self.floor_filter_combo.currentText() != "Tümü":
                        where_clauses.append("json_extract(data, '$[9]') = ?")
                        params.append(self.floor_filter_combo.currentText())
                    where_sql = " WHERE " + " AND ".join(where_clauses) if where_clauses else ""

                    cursor.execute(f"SELECT COUNT(*) FROM inventory{where_sql}", params)
                    total_records = cursor.fetchone()[0]
                    cursor.execute(f"SELECT json_extract(data, '$[1]'), COUNT(*) FROM inventory{where_sql} GROUP BY json_extract(data, '$[1]')", params)
                    group_dist = cursor.fetchall()
                    cursor.execute(f"SELECT json_extract(data, '$[8]'), COUNT(*) FROM inventory{where_sql} GROUP BY json_extract(data, '$[8]')", params)
                    region_dist = cursor.fetchall()
                    cursor.execute(f"SELECT json_extract(data, '$[9]'), COUNT(*) FROM inventory{where_sql} GROUP BY json_extract(data, '$[9]')", params)
                    floor_dist = cursor.fetchall()
                    cursor.execute(f"SELECT strftime('%Y-%m', timestamp), COUNT(*) FROM inventory{where_sql} GROUP BY strftime('%Y-%m', timestamp)", params)
                    time_dist = cursor.fetchall()
                    cursor.execute(f"SELECT AVG(CAST(json_extract(data, '$[4]') AS REAL)) FROM inventory{where_sql} WHERE json_extract(data, '$[4]') != ''", params)
                    avg_cost = round(cursor.fetchone()[0] or 0.0, 2)
                    cursor.execute(f"SELECT json_extract(data, '$[6]') FROM inventory{where_sql} WHERE json_extract(data, '$[6]') != ''", params)
                    warranty_dates = cursor.fetchall()
                    current_date = datetime.now()
                    active_warranties = sum(1 for date_str in warranty_dates if date_str[0] and date_str[0] != TRANSLATIONS["unknown"] and datetime.strptime(date_str[0], "%d.%m.%Y") > current_date)
                    expired_warranties = len(warranty_dates) - active_warranties
                    cursor.execute(f"SELECT data FROM inventory{where_sql}", params)
                    detail_data = [json.loads(row[0]) for row in cursor.fetchall()]
                    headers = self.get_column_headers()

                    if file_name.endswith(".xlsx"):
                        with pd.ExcelWriter(file_name, engine='xlsxwriter', options={'encoding': 'utf-8'}) as writer:
                            workbook = writer.book
                            format = workbook.add_format({'font_name': 'Arial'})
                            if export_overview.isChecked():
                                df_overview = pd.DataFrame({
                                    "Metrik": ["Toplam Kayıt Sayısı", "Ortalama Alış Bedeli", "Aktif Garantili Ürünler", "Garantisi Bitmiş Ürünler"],
                                    "Değer": [total_records, f"{avg_cost} TL", active_warranties, expired_warranties]
                                })
                                df_overview.to_excel(writer, sheet_name="Genel Bakış", index=False)
                                worksheet = writer.sheets["Genel Bakış"]
                                for col_num, value in enumerate(df_overview.columns.values):
                                    worksheet.write(0, col_num, value, format)
                            if export_groups.isChecked():
                                df_groups = pd.DataFrame(group_dist, columns=["Grup", "Sayı"])
                                df_groups.to_excel(writer, sheet_name="Grup Dağılımı", index=False)
                                worksheet = writer.sheets["Grup Dağılımı"]
                                for col_num, value in enumerate(df_groups.columns.values):
                                    worksheet.write(0, col_num, value, format)
                            if export_regions.isChecked():
                                df_regions = pd.DataFrame(region_dist, columns=["Bölge", "Sayı"])
                                df_regions.to_excel(writer, sheet_name="Bölge Dağılımı", index=False)
                                worksheet = writer.sheets["Bölge Dağılımı"]
                                for col_num, value in enumerate(df_regions.columns.values):
                                    worksheet.write(0, col_num, value, format)
                            if export_floors.isChecked():
                                df_floors = pd.DataFrame(floor_dist, columns=["Kat", "Sayı"])
                                df_floors.to_excel(writer, sheet_name="Kat Dağılımı", index=False)
                                worksheet = writer.sheets["Kat Dağılımı"]
                                for col_num, value in enumerate(df_floors.columns.values):
                                    worksheet.write(0, col_num, value, format)
                            if export_time.isChecked():
                                df_time = pd.DataFrame(time_dist, columns=["Ay", "Sayı"])
                                df_time.to_excel(writer, sheet_name="Zaman Analizi", index=False)
                                worksheet = writer.sheets["Zaman Analizi"]
                                for col_num, value in enumerate(df_time.columns.values):
                                    worksheet.write(0, col_num, value, format)
                            if export_details.isChecked():
                                df_details = pd.DataFrame(detail_data, columns=headers)
                                df_details.to_excel(writer, sheet_name="Detaylı Veri", index=False)
                                worksheet = writer.sheets["Detaylı Veri"]
                                for col_num, value in enumerate(df_details.columns.values):
                                    worksheet.write(0, col_num, value, format)
                        QMessageBox.information(self, "Başarılı", "Analiz Excel'e aktarıldı!")
                        logging.info(f"Analiz {file_name} dosyasına Excel formatında aktarıldı.")

                    elif file_name.endswith(".pdf"):
                        doc = SimpleDocTemplate(file_name, pagesize=landscape(A4))
                        elements = []
                        styles = getSampleStyleSheet()

                        title_style = styles['Heading1']
                        title_style.alignment = 1
                        title_style.fontName = self.default_font
                        normal_style = styles['Normal']
                        normal_style.fontName = self.default_font
                        normal_style.fontSize = 10
                        heading2_style = styles['Heading2']
                        heading2_style.fontName = self.default_font

                        if os.path.exists(LOGO_FILE):
                            logo = Image(LOGO_FILE, width=2 * cm, height=2 * cm)
                            elements.append(logo)
                            elements.append(Spacer(1, 0.2 * cm))
                        elements.append(Paragraph(TRANSLATIONS["title"], title_style))
                        elements.append(Paragraph(TRANSLATIONS["analysis_title"], heading2_style))
                        elements.append(Spacer(1, 0.5 * cm))

                        info_text = (
                            "Galatasaraylılar Yurdu Envanter Kayıt Sistemi\n"
                            f"Tarih: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n"
                            "Adres: Florya, Şenlikköy Mh. Orman Sk. No:39/1 Florya Bakırköy/İstanbul\n"
                            "E-posta: bilgi@gsyardimlasmavakfi.org\n"
                            "Telefon: (0212) 574 52 55"
                        )
                        elements.append(Paragraph(info_text, normal_style))
                        elements.append(Spacer(1, 0.5 * cm))

                        if export_overview.isChecked():
                            elements.append(Paragraph("Genel Bakış", heading2_style))
                            overview_data = [["Metrik", "Değer"]] + [
                                ["Toplam Kayıt Sayısı", str(total_records)],
                                ["Ortalama Alış Bedeli", f"{avg_cost} TL"],
                                ["Aktif Garantili Ürünler", str(active_warranties)],
                                ["Garantisi Bitmiş Ürünler", str(expired_warranties)]
                            ]
                            table = Table(overview_data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.5 * cm))

                        if export_groups.isChecked():
                            elements.append(Paragraph("Grup Dağılımı", heading2_style))
                            group_data = [["Grup", "Sayı"]] + [[str(row[0]), str(row[1])] for row in group_dist]
                            table = Table(group_data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.5 * cm))

                        if export_regions.isChecked():
                            elements.append(Paragraph("Bölge Dağılımı", heading2_style))
                            region_data = [["Bölge", "Sayı"]] + [[str(row[0]), str(row[1])] for row in region_dist]
                            table = Table(region_data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.5 * cm))

                        if export_floors.isChecked():
                            elements.append(Paragraph("Kat Dağılımı", heading2_style))
                            floor_data = [["Kat", "Sayı"]] + [[str(row[0]), str(row[1])] for row in floor_dist]
                            table = Table(floor_data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.5 * cm))

                        if export_time.isChecked():
                            elements.append(Paragraph("Zaman Analizi", heading2_style))
                            time_data = [["Ay", "Sayı"]] + [[str(row[0]), str(row[1])] for row in time_dist]
                            table = Table(time_data)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                                ('FONTSIZE', (0, 0), (-1, -1), 10),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.5 * cm))

                        if export_details.isChecked():
                            elements.append(Paragraph("Detaylı Veri", heading2_style))
                            detail_data_table = [headers] + [[str(item) for item in row] for row in detail_data]
                            table = Table(detail_data_table)
                            table.setStyle(TableStyle([
                                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                                ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                                ('FONTSIZE', (0, 0), (-1, -1), 8),
                                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                            ]))
                            elements.append(table)
                            elements.append(Spacer(1, 0.5 * cm))

                        footer_text = Paragraph(TRANSLATIONS["about_copyright"], normal_style)
                        footer_text.alignment = 1
                        elements.append(footer_text)

                        logging.info(f"PDF export using font: {self.default_font}")
                        doc.build(elements)
                        QMessageBox.information(self, "Başarılı", "Analiz PDF olarak kaydedildi!")
                        logging.info(f"Analiz {file_name} dosyasına PDF formatında aktarıldı.")

                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"Analiz dışa aktarma başarısız: {str(e)}")
                    logging.error(f"Analiz dışa aktarma hatası: {str(e)}")

    def manual_backup(self):
        backup_dir = self.config["backup_path"]
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"inventory_backup_{timestamp}.db")
        shutil.copy(DB_FILE, backup_file)
        QMessageBox.information(self, "Başarılı", TRANSLATIONS["db_backed_up"])
        logging.info(f"Manuel yedekleme yapıldı: {backup_file}")

    def auto_backup(self):
        backup_dir = self.config["backup_path"]
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"inventory_backup_{timestamp}.db")
        shutil.copy(DB_FILE, backup_file)
        now = time.time()
        cutoff = now - (self.config["backup_retention"] * 86400)
        for backup_file in glob.glob(os.path.join(backup_dir, "inventory_backup_*.db")):
            if os.path.getctime(backup_file) < cutoff:
                os.remove(backup_file)
        logging.info(f"Otomatik yedekleme yapıldı: {backup_file}")

    def save_current_form(self):
        pass

    def add_parameter(self):
        dialog = AddParameterDialog(self)
        if dialog.exec_():
            name, section = dialog.get_data()
            if not name:
                QMessageBox.warning(self, "Hata", "Parametre adı boş olamaz!")
                return
            cursor = self.conn.cursor()
            cursor.execute("SELECT MAX(column_order) FROM metadata")
            max_order = cursor.fetchone()[0] or 0
            cursor.execute("INSERT INTO metadata (column_name, column_order, section) VALUES (?, ?, ?)",
                           (name, max_order + 1, section))
            self.conn.commit()

            if section == TRANSLATIONS["card_info"]:
                if "grup" in name.lower():
                    self.update_json_with_shortcode(name, self.groups, GROUPS_FILE, action="add")
                elif "bölge" in name.lower() or "oda" in name.lower():
                    self.update_json_with_shortcode(name, self.regions, REGIONS_FILE, action="add")
                elif "kat" in name.lower():
                    self.update_json_with_shortcode(name, self.floors, FLOORS_FILE, action="add")
                self.update_comboboxes()

            self.setup_inventory_tab()
            self.setup_archive_tab()
            self.load_data_from_db()
            self.load_archive_from_db()
            QMessageBox.information(self, "Başarılı", "Yeni parametre eklendi.")

    def delete_parameter(self):
        headers = self.get_column_headers()
        name, ok = QInputDialog.getItem(self, TRANSLATIONS["delete_parameter"],
                                        "Silinecek Parametre:", headers, 0, False)
        if ok and name != "Kod":
            cursor = self.conn.cursor()
            cursor.execute("DELETE FROM metadata WHERE column_name = ?", (name,))
            cursor.execute("SELECT id, data FROM inventory")
            rows = cursor.fetchall()
            deleted_index = headers.index(name)
            for row_id, row_data in rows:
                data = json.loads(row_data)
                if len(data) > deleted_index:
                    data.pop(deleted_index)
                cursor.execute("UPDATE inventory SET data = ? WHERE id = ?", (json.dumps(data), row_id))
            cursor.execute("SELECT id, data FROM archive")
            archive_rows = cursor.fetchall()
            for row_id, row_data in archive_rows:
                data = json.loads(row_data)
                if len(data) > deleted_index:
                    data.pop(deleted_index)
                cursor.execute("UPDATE archive SET data = ? WHERE id = ?", (json.dumps(data), row_id))
            self.conn.commit()

            if "grup" in name.lower():
                self.update_json_with_shortcode(name, self.groups, GROUPS_FILE, action="delete")
            elif "bölge" in name.lower() or "oda" in name.lower():
                self.update_json_with_shortcode(name, self.regions, REGIONS_FILE, action="delete")
            elif "kat" in name.lower():
                self.update_json_with_shortcode(name, self.floors, FLOORS_FILE, action="delete")
            self.update_comboboxes()

            self.setup_inventory_tab()
            self.setup_archive_tab()
            self.load_data_from_db()
            self.load_archive_from_db()
            QMessageBox.information(self, "Başarılı", "Parametre silindi!")
        elif name == "Kod":
            QMessageBox.warning(self, "Hata", "'Kod' sütunu silinemez!")

    def edit_parameter(self):
        headers = self.get_column_headers()
        current_name, ok = QInputDialog.getItem(self, TRANSLATIONS["edit_parameter"],
                                                "Düzenlenecek Parametre:", headers, 0, False)
        if ok and current_name != "Kod":
            dialog = EditParameterDialog(self, current_name)
            if dialog.exec_():
                new_name, section = dialog.get_data()
                if not new_name:
                    QMessageBox.warning(self, "Hata", "Yeni parametre adı boş olamaz!")
                    return
                cursor = self.conn.cursor()
                cursor.execute("UPDATE metadata SET column_name = ?, section = ? WHERE column_name = ?",
                               (new_name, section, current_name))
                cursor.execute("SELECT id, data FROM inventory")
                rows = cursor.fetchall()
                index = headers.index(current_name)
                for row_id, row_data in rows:
                    data = json.loads(row_data)
                    if len(data) > index:
                        cursor.execute("UPDATE inventory SET data = ? WHERE id = ?",
                                       (json.dumps(data), row_id))
                cursor.execute("SELECT id, data FROM archive")
                archive_rows = cursor.fetchall()
                for row_id, row_data in archive_rows:
                    data = json.loads(row_data)
                    if len(data) > index:
                        cursor.execute("UPDATE archive SET data = ? WHERE id = ?",
                                       (json.dumps(data), row_id))
                self.conn.commit()

                if "grup" in current_name.lower():
                    self.update_json_with_shortcode(current_name, self.groups, GROUPS_FILE, action="delete")
                    self.update_json_with_shortcode(new_name, self.groups, GROUPS_FILE, action="add")
                elif "bölge" in current_name.lower() or "oda" in current_name.lower():
                    self.update_json_with_shortcode(current_name, self.regions, REGIONS_FILE, action="delete")
                    self.update_json_with_shortcode(new_name, self.regions, REGIONS_FILE, action="add")
                elif "kat" in current_name.lower():
                    self.update_json_with_shortcode(current_name, self.floors, FLOORS_FILE, action="delete")
                    self.update_json_with_shortcode(new_name, self.floors, FLOORS_FILE, action="add")
                self.update_comboboxes()

                self.setup_inventory_tab()
                self.setup_archive_tab()
                self.load_data_from_db()
                self.load_archive_from_db()
                QMessageBox.information(self, "Başarılı", "Parametre güncellendi!")
        elif current_name == "Kod":
            QMessageBox.warning(self, "Hata", "'Kod' sütunu düzenlenemez!")

    def edit_combobox(self, title, items, file_path):
        dialog = ComboBoxEditDialog(self, title, items, file_path)
        dialog.exec_()

    def quick_search(self):
        search_text = self.search_bar.text().lower()
        for row in range(self.table.rowCount()):
            row_hidden = True
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and search_text in item.text().lower():
                    row_hidden = False
                    break
            self.table.setRowHidden(row, row_hidden)

    def filter_data(self):
        filter_group = self.filter_combo.currentText()
        for row in range(self.table.rowCount()):
            group_item = self.table.item(row, 1)
            if filter_group == "Tümü" or (group_item and group_item.text() == filter_group):
                self.table.setRowHidden(row, False)
            else:
                self.table.setRowHidden(row, True)

    def create_or_update_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           data TEXT,
                           timestamp TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS archive (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           data TEXT,
                           timestamp TEXT)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (
                           id INTEGER PRIMARY KEY AUTOINCREMENT,
                           column_name TEXT,
                           column_order INTEGER,
                           section TEXT)''')
        self.conn.commit()

        cursor.execute("SELECT COUNT(*) FROM metadata")
        if cursor.fetchone()[0] == 0:
            default_columns = [
                ("Kod", 0, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["group_name"], 1, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["item_name"], 2, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["purchase_date"], 3, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["purchase_cost"], 4, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["cost_center"], 5, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["user"], 6, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["region"], 7, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["floor"], 8, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["invoice_no"], 9, TRANSLATIONS["invoice_info"]),
                (TRANSLATIONS["quantity"], 10, TRANSLATIONS["invoice_info"]),
                (TRANSLATIONS["company"], 11, TRANSLATIONS["invoice_info"]),
                (TRANSLATIONS["description"], 12, TRANSLATIONS["invoice_info"]),
                (TRANSLATIONS["brand"], 13, TRANSLATIONS["service_info"]),
                (TRANSLATIONS["model"], 14, TRANSLATIONS["service_info"]),
                (TRANSLATIONS["warranty_period"], 15, TRANSLATIONS["service_info"]),
                (TRANSLATIONS["status"], 16, TRANSLATIONS["service_info"]),
                (TRANSLATIONS["note"], 17, TRANSLATIONS["service_info"])
            ]
            cursor.executemany("INSERT INTO metadata (column_name, column_order, section) VALUES (?, ?, ?)", default_columns)
            self.conn.commit()
            logging.info("Metadata tablosu varsayılan sütunlarla dolduruldu.")
        else:
            cursor.execute("SELECT column_order FROM metadata WHERE column_name = 'Kod'")
            result = cursor.fetchone()
            if result is None:
                cursor.execute("INSERT INTO metadata (column_name, column_order, section) VALUES (?, ?, ?)",
                               ("Kod", 0, TRANSLATIONS["card_info"]))
                cursor.execute("UPDATE metadata SET column_order = column_order + 1 WHERE column_name != 'Kod'")
            elif result[0] != 0:
                cursor.execute("UPDATE metadata SET column_order = column_order + 1 WHERE column_name != 'Kod'")
                cursor.execute("UPDATE metadata SET column_order = 0 WHERE column_name = 'Kod'")
            self.conn.commit()

    def get_column_headers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name FROM metadata ORDER BY column_order")
        headers = [row[0] for row in cursor.fetchall()]
        if not headers:
            headers = [
                "Kod",
                TRANSLATIONS["group_name"],
                TRANSLATIONS["item_name"],
                TRANSLATIONS["purchase_date"],
                TRANSLATIONS["purchase_cost"],
                TRANSLATIONS["cost_center"],
                TRANSLATIONS["user"],
                TRANSLATIONS["region"],
                TRANSLATIONS["floor"],
                TRANSLATIONS["invoice_no"],
                TRANSLATIONS["quantity"],
                TRANSLATIONS["company"],
                TRANSLATIONS["description"],
                TRANSLATIONS["brand"],
                TRANSLATIONS["model"],
                TRANSLATIONS["warranty_period"],
                TRANSLATIONS["status"],
                TRANSLATIONS["note"]
            ]
        return headers

    def close_application(self):
        self.conn.close()
        QApplication.quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())