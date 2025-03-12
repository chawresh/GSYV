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
from PyQt5.QtGui import QFont, QPixmap, QTextOption, QCursor
import os
import shutil
import logging
import glob
import time
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
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
    "group_distribution": "Demirbaş Cinsi Dağılımı",
    "status_distribution": "Durum Dağılımı",
    "region_distribution": "Lokasyon Dağılımı",
    "brand_distribution": "Marka Dağılımı",
    "warranty_status": "Garanti Durumu",
    "search_placeholder": "Tabloda Ara...",
    "filter_group": "Demirbaş Cinsine Göre Filtrele:",
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
    "group_name": "Demirbaş Cinsi",
    "item_name": "Demirbaş Adı",
    "region": "Lokasyon",
    "quantity": "Miktar",
    "brand": "Marka",
    "model": "Model",
    "invoice_no": "Fatura No",
    "company": "Firma",
    "description": "Açıklama",
    "warranty_period": "Garanti Süresi",
    "status": "Durum",
    "floor": "Kat",
    "photo": "Demirbaş Fotoğrafı",
    "no_photo": "Fotoğraf Yok",
    "edit_groups": "Demirbaş Cinsi Düzenle",
    "edit_regions": "Lokasyon Düzenle",
    "edit_floors": "Kat Düzenle",
    "combobox_management": "ComboBox Yönetimi",
    "add_new_item": "Yeni Ekle",
    "edit_selected_item": "Seçileni Düzenle",
    "delete_selected_item": "Seçileni Sil",
    "unknown": "Bilinmiyor",
    "no_donor": "Bağışçı Yok",
    "new_combobox_param": "Yeni ComboBox Parametresi Ekle",
    "param_type": "Parametre Türü:",
    "combobox_file": "ComboBox Veri Dosyası:",
    "export_charts": "Grafikleri Dışa Aktar",
    "export_analysis_data": "Analiz Verilerini Dışa Aktar"
}

DEFAULT_GROUPS = [
    {"name": "Genel", "code": "GEN"},
    {"name": "Mobilya", "code": "MOB"},
    {"name": "Mutfak", "code": "MUT"},
    {"name": "Elektronik", "code": "ELK"},
    {"name": "Bakım Malzemesi", "code": "BAK"},
    {"name": "Temizlik", "code": "TEM"}
]
DEFAULT_REGIONS = [
    {"name": "Salon", "code": "SAL"},
    {"name": "Mutfak", "code": "MUT"},
    {"name": "Müdür Odası", "code": "MOD"},
    {"name": "Teras", "code": "TER"}
]
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
        self.param_types = ["Metin", "ComboBox", "Tarih"]

        layout = QFormLayout(self)
        label = QLabel("Parametre Adı *")
        entry = QLineEdit()
        entry.setPlaceholderText("Ör: Özellikler")
        self.entries["Parameter Name"] = entry
        layout.addRow(label, entry)

        section_label = QLabel(TRANSLATIONS["select_section"])
        self.section_combo = QComboBox()
        self.section_combo.addItems(self.sections)
        layout.addRow(section_label, self.section_combo)

        type_label = QLabel(TRANSLATIONS["param_type"])
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.param_types)
        layout.addRow(type_label, self.type_combo)

        file_label = QLabel(TRANSLATIONS["combobox_file"])
        self.file_entry = QLineEdit()
        self.file_entry.setEnabled(False)
        self.type_combo.currentTextChanged.connect(self.toggle_file_entry)
        layout.addRow(file_label, self.file_entry)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def toggle_file_entry(self, text):
        self.file_entry.setEnabled(text == "ComboBox")

    def get_data(self):
        return (self.entries["Parameter Name"].text().strip(), 
                self.section_combo.currentText(), 
                self.type_combo.currentText(), 
                self.file_entry.text().strip() if self.type_combo.currentText() == "ComboBox" else None)

class EditParameterDialog(QDialog):
    def __init__(self, parent=None, current_name=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSLATIONS["edit_parameter"])
        self.parent = parent
        self.current_name = current_name
        self.sections = ["Kart Bilgileri", "Fatura Bilgileri", "Servis Bilgileri"]
        self.param_types = ["Metin", "ComboBox", "Tarih"]

        layout = QFormLayout(self)
        label = QLabel("Yeni Parametre Adı *")
        self.name_entry = QLineEdit(current_name)
        layout.addRow(label, self.name_entry)

        section_label = QLabel(TRANSLATIONS["select_section"])
        self.section_combo = QComboBox()
        self.section_combo.addItems(self.sections)
        layout.addRow(section_label, self.section_combo)

        type_label = QLabel(TRANSLATIONS["param_type"])
        self.type_combo = QComboBox()
        self.type_combo.addItems(self.param_types)
        layout.addRow(type_label, self.type_combo)

        file_label = QLabel(TRANSLATIONS["combobox_file"])
        self.file_entry = QLineEdit()
        self.file_entry.setEnabled(False)
        self.type_combo.currentTextChanged.connect(self.toggle_file_entry)
        layout.addRow(file_label, self.file_entry)

        if self.parent.conn:
            cursor = self.parent.conn.cursor()
            cursor.execute("SELECT section, type, combobox_file FROM metadata WHERE column_name = ?", (current_name,))
            result = cursor.fetchone()
            if result:
                section, param_type, combobox_file = result
                self.section_combo.setCurrentText(section)
                self.type_combo.setCurrentText(param_type)
                if combobox_file:
                    self.file_entry.setText(combobox_file)
                    self.file_entry.setEnabled(param_type == "ComboBox")

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def toggle_file_entry(self, text):
        self.file_entry.setEnabled(text == "ComboBox")

    def get_data(self):
        return (self.name_entry.text().strip(), 
                self.section_combo.currentText(), 
                self.type_combo.currentText(), 
                self.file_entry.text().strip() if self.type_combo.currentText() == "ComboBox" else None)

class ComboBoxEditDialog(QDialog):
    def __init__(self, parent=None, title="", items=None, file_path=""):
        super().__init__(parent)
        self.setWindowTitle(title)
        self.parent = parent
        self.items = items.copy() if items else []
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
        self.headers = headers or []
        self.entries = {}

        # Veritabanından tam veriyi al
        cursor = self.parent.conn.cursor()
        
        # row_data'nın türüne göre row_id ve veri işleme
        if row_data:
            if isinstance(row_data[0], QTableWidgetItem):  # Tablo öğesi ise
                row_id = row_data[0].data(Qt.UserRole)
                cursor.execute("SELECT data FROM inventory WHERE id = ?", (row_id,))
                full_data = json.loads(cursor.fetchone()[0])
            elif isinstance(row_data[0], str):  # String listesi ise (restore_archive_item'dan gelir)
                full_data = row_data
                row_id = None  # restore_archive_item zaten full_data'yı sağlıyor, row_id gerekmeyebilir
            else:
                raise ValueError("EditDialog: row_data beklenmeyen bir türde.")
        else:
            full_data = [""] * len(self.headers)
            row_id = None
            logging.warning("EditDialog: row_data None, boş veri seti kullanılıyor.")

        # full_data'nın headers ile uyumlu olduğundan emin olalım
        self.row_data = full_data if len(full_data) >= len(self.headers) else full_data + [""] * (len(self.headers) - len(full_data))
        if len(self.row_data) > len(self.headers):
            self.row_data = self.row_data[:len(self.headers)]

        logging.info(f"EditDialog: headers={self.headers}")
        logging.info(f"EditDialog: row_data={self.row_data}")

        layout = QFormLayout(self)
        cursor.execute("SELECT column_name, type, combobox_file FROM metadata ORDER BY column_order")
        metadata = cursor.fetchall()
        param_types = {row[0]: (row[1], row[2]) for row in metadata}

        for i, header in enumerate(self.headers):
            label = QLabel(header)
            param_type, combobox_file = param_types.get(header, ("Metin", None))
            current_value = self.row_data[i]
            logging.info(f"EditDialog: '{header}' için current_value={current_value}, param_type={param_type}")

            if header == "Demirbaş Kodu":
                entry = QLineEdit(current_value)
                entry.setReadOnly(True)
                self.entries[header] = entry
            elif param_type == "ComboBox" and combobox_file:
                combo = QComboBox()
                items = self.parent.load_json_data(combobox_file, [])
                combo.addItems([item["name"] for item in items])
                combo.setCurrentText(current_value)
                combo.setEditable(True)
                self.entries[header] = combo
            elif param_type == "Tarih":
                date_layout = QHBoxLayout()
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                try:
                    if current_value and current_value != TRANSLATIONS["unknown"]:
                        date_edit.setDate(datetime.strptime(current_value, "%d.%m.%Y"))
                    else:
                        date_edit.setDate(datetime.now())
                except ValueError:
                    date_edit.setDate(datetime.now())
                self.entries[header] = date_edit
                unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                unknown_check.setChecked(current_value == TRANSLATIONS["unknown"])
                unknown_check.stateChanged.connect(lambda state, de=date_edit: self.toggle_date(de, state))
                date_layout.addWidget(date_edit)
                date_layout.addWidget(unknown_check)
                self.entries[f"{header}_check"] = unknown_check
                layout.addRow(label, date_layout)
                continue
            elif header == "Bağışçı":
                donor_layout = QHBoxLayout()
                entry = QLineEdit(current_value)
                self.entries[header] = entry
                no_donor_check = QCheckBox(TRANSLATIONS["no_donor"])
                no_donor_check.setChecked(not current_value)
                no_donor_check.stateChanged.connect(lambda state, e=entry: self.toggle_donor(e, state))
                donor_layout.addWidget(entry)
                donor_layout.addWidget(no_donor_check)
                self.entries[f"{header}_check"] = no_donor_check
                layout.addRow(label, donor_layout)
                continue
            elif header == TRANSLATIONS["photo"]:
                photo_layout = QHBoxLayout()
                entry = QLineEdit(current_value)
                entry.setReadOnly(True)
                self.entries[header] = entry
                browse_button = QPushButton("Dosya Seç")
                browse_button.clicked.connect(lambda: self.select_photo(entry))
                photo_layout.addWidget(entry)
                photo_layout.addWidget(browse_button)
                no_photo_check = QCheckBox(TRANSLATIONS["no_photo"])
                no_photo_check.setChecked(not current_value)
                no_photo_check.stateChanged.connect(lambda state, e=entry: self.toggle_photo(e, state))
                photo_layout.addWidget(no_photo_check)
                self.entries[f"{header}_check"] = no_photo_check
                layout.addRow(label, photo_layout)
                continue
            elif header == "Özellikler":
                entry = QTextEdit(current_value)
                entry.setAcceptRichText(False)
                entry.setMaximumHeight(90)
                self.entries[header] = entry
            elif header == TRANSLATIONS["description"]:
                entry = QTextEdit(current_value)
                entry.setAcceptRichText(False)
                entry.setMaximumHeight(75)
                self.entries[header] = entry
            else:
                entry = QLineEdit(current_value)
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

    def toggle_donor(self, entry, state):
        entry.setEnabled(state == Qt.Unchecked)
        if state == Qt.Checked:
            entry.clear()

    def toggle_photo(self, entry, state):
        entry.setEnabled(state == Qt.Unchecked)
        if state == Qt.Checked:
            entry.clear()

    def select_photo(self, entry):
        file_name, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if file_name:
            entry.setText(file_name)
            logging.info(f"EditDialog'da 'Demirbaş Fotoğrafı' için seçilen dosya: {file_name}")

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
                elif header == "Bağışçı" and f"{header}_check" in self.entries and self.entries[f"{header}_check"].isChecked():
                    value = ""
                elif header == TRANSLATIONS["photo"] and f"{header}_check" in self.entries and self.entries[f"{header}_check"].isChecked():
                    value = ""
                else:
                    value = self.entries[header].text()
                data.append(value)
            else:
                data.append("")
                logging.warning(f"EditDialog'da '{header}' için entry bulunamadı.")
        logging.info(f"EditDialog: Güncellenmiş veri={data}")
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
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(default_data, f, ensure_ascii=False, indent=4)
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

    def update_comboboxes(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name, combobox_file FROM metadata WHERE type = 'ComboBox'")
        combobox_params = cursor.fetchall()

        for header, file_path in combobox_params:
            if header in self.card_entries:
                combo = self.card_entries[header]
                items = self.load_json_data(file_path, [])
                current_text = combo.currentText()
                combo.clear()
                combo.addItems([item["name"] for item in items])
                combo.setCurrentText(current_text)
            elif header in self.invoice_entries:
                combo = self.invoice_entries[header]
                items = self.load_json_data(file_path, [])
                current_text = combo.currentText()
                combo.clear()
                combo.addItems([item["name"] for item in items])
                combo.setCurrentText(current_text)
            elif header in self.service_entries:
                combo = self.service_entries[header]
                items = self.load_json_data(file_path, [])
                current_text = combo.currentText()
                combo.clear()
                combo.addItems([item["name"] for item in items])
                combo.setCurrentText(current_text)

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

        group_code = get_or_add_code(self.groups, GROUPS_FILE, group_name, [item["code"] for item in self.groups])
        region_code = get_or_add_code(self.regions, REGIONS_FILE, region_name, [item["code"] for item in self.regions])
        floor_code = get_or_add_code(self.floors, FLOORS_FILE, floor_name, [item["code"] for item in self.floors])
        code = f"{group_code}-{region_code}-{floor_code}"
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
            region_name = next((item["name"] for item in self.regions if item["code"] == region_code), "Bilinmeyen Lokasyon")
            floor_name = next((item["name"] for item in self.floors if item["code"] == floor_code), "Bilinmeyen Kat")
            
            if "Bilinmeyen" in [group_name, region_name, floor_name]:
                return f"Kod çözümleme başarısız: '{code}'. Grup: {group_name}, Lokasyon: {region_name}, Kat: {floor_name}."

            return f"Demirbaş Cinsi: {group_name}, Lokasyon: {region_name}, Kat: {floor_name}"
        except Exception as e:
            logging.error(f"Kod çözümleme hatası: {str(e)}, Kod: {code}")
            return f"Kod çözümleme hatası: {str(e)}"

    def setup_inventory_tab(self):
        if not hasattr(self, 'card_entries'):
            self.card_entries = {}
            self.invoice_entries = {}
            self.service_entries = {}

        if self.inventory_tab.layout() is None:
            self.inventory_tab.setLayout(QVBoxLayout())

        layout = self.inventory_tab.layout()
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

        top_layout = QHBoxLayout()

        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name, section, type, combobox_file FROM metadata ORDER BY column_order")
        metadata = cursor.fetchall()
        if not metadata:
            self.create_or_update_tables()
            cursor.execute("SELECT column_name, section, type, combobox_file FROM metadata ORDER BY column_order")
            metadata = cursor.fetchall()

        card_headers = [row[0] for row in metadata if row[1] == TRANSLATIONS["card_info"]]
        invoice_headers = [row[0] for row in metadata if row[1] == TRANSLATIONS["invoice_info"]]
        service_headers = [row[0] for row in metadata if row[1] == TRANSLATIONS["service_info"]]

        self.card_group = QGroupBox(TRANSLATIONS["card_info"])
        self.card_layout = QFormLayout()
        for header, _, param_type, combobox_file in [(row[0], row[1], row[2], row[3]) for row in metadata if row[1] == TRANSLATIONS["card_info"]]:
            label = QLabel(header + (" *" if header == TRANSLATIONS["item_name"] else ""))
            if header not in self.card_entries:
                if header == "Demirbaş Kodu":
                    entry = QLineEdit("Otomatik")
                    entry.setReadOnly(True)
                    self.card_entries[header] = entry
                elif header == TRANSLATIONS["photo"]:
                    photo_layout = QHBoxLayout()
                    entry = QLineEdit()
                    entry.setReadOnly(True)
                    self.card_entries[header] = entry
                    browse_button = QPushButton("Dosya Seç")
                    browse_button.clicked.connect(lambda checked, e=entry: self.select_photo(e))
                    photo_layout.addWidget(entry)
                    photo_layout.addWidget(browse_button)
                    no_photo_check = QCheckBox(TRANSLATIONS["no_photo"])
                    no_photo_check.stateChanged.connect(lambda state, e=entry: self.toggle_photo(e, state))
                    photo_layout.addWidget(no_photo_check)
                    self.card_entries[f"{header}_check"] = no_photo_check
                    self.card_layout.addRow(label, photo_layout)
                    continue
                elif header == TRANSLATIONS["group_name"]:
                    combo = QComboBox()
                    combo.addItems([item["name"] for item in self.groups])
                    combo.setEditable(True)
                    if self.config["startup_group"] != "Son Kullanılan" and self.config["startup_group"] in [item["name"] for item in self.groups]:
                        combo.setCurrentText(self.config["startup_group"])
                    self.card_entries[header] = combo
                elif header == TRANSLATIONS["region"]:
                    combo = QComboBox()
                    combo.addItems([item["name"] for item in self.regions])
                    combo.setEditable(True)
                    self.card_entries[header] = combo
                elif header == TRANSLATIONS["floor"]:
                    combo = QComboBox()
                    combo.addItems([item["name"] for item in self.floors])
                    combo.setEditable(True)
                    self.card_entries[header] = combo
                elif param_type == "Tarih":
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
                else:
                    entry = QLineEdit()
                    self.card_entries[header] = entry
            self.card_layout.addRow(label, self.card_entries[header])
        self.card_group.setLayout(self.card_layout)
        top_layout.addWidget(self.card_group)

        self.invoice_group = QGroupBox(TRANSLATIONS["invoice_info"])
        self.invoice_layout = QFormLayout()
        for header, _, param_type, combobox_file in [(row[0], row[1], row[2], row[3]) for row in metadata if row[1] == TRANSLATIONS["invoice_info"]]:
            label = QLabel(header)
            if header not in self.invoice_entries:
                if header == "Bağışçı":
                    donor_layout = QHBoxLayout()
                    entry = QLineEdit()
                    self.invoice_entries[header] = entry
                    no_donor_check = QCheckBox(TRANSLATIONS["no_donor"])
                    no_donor_check.stateChanged.connect(lambda state, e=entry: self.toggle_donor(e, state))
                    donor_layout.addWidget(entry)
                    donor_layout.addWidget(no_donor_check)
                    self.invoice_entries[f"{header}_check"] = no_donor_check
                    self.invoice_layout.addRow(label, donor_layout)
                    continue
                elif header == "Özellikler":
                    entry = QTextEdit()
                    entry.setAcceptRichText(False)
                    entry.setMaximumHeight(90)
                    self.invoice_entries[header] = entry
                elif param_type == "ComboBox" and combobox_file:
                    combo = QComboBox()
                    items = self.load_json_data(combobox_file, [])
                    combo.addItems([item["name"] for item in items])
                    combo.setEditable(True)
                    self.invoice_entries[header] = combo
                elif param_type == "Tarih":
                    date_layout = QHBoxLayout()
                    date_edit = QDateEdit()
                    date_edit.setCalendarPopup(True)
                    date_edit.setDisplayFormat("dd.MM.yyyy")
                    date_edit.setDate(datetime.now().date())
                    self.invoice_entries[header] = date_edit
                    unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                    unknown_check.stateChanged.connect(lambda state, de=date_edit: de.setEnabled(state == Qt.Unchecked))
                    date_layout.addWidget(date_edit)
                    date_layout.addWidget(unknown_check)
                    self.invoice_entries[f"{header}_check"] = unknown_check
                    self.invoice_layout.addRow(label, date_layout)
                    continue
                else:
                    entry = QLineEdit()
                    self.invoice_entries[header] = entry
            self.invoice_layout.addRow(label, self.invoice_entries[header])
        self.invoice_group.setLayout(self.invoice_layout)
        top_layout.addWidget(self.invoice_group)

        self.service_group = QGroupBox(TRANSLATIONS["service_info"])
        self.service_layout = QFormLayout()
        for header, _, param_type, combobox_file in [(row[0], row[1], row[2], row[3]) for row in metadata if row[1] == TRANSLATIONS["service_info"]]:
            label = QLabel(header)
            if header not in self.service_entries:
                if header == TRANSLATIONS["warranty_period"]:
                    date_layout = QHBoxLayout()
                    date_edit = QDateEdit()
                    date_edit.setCalendarPopup(True)
                    date_edit.setDisplayFormat("dd.MM.yyyy")
                    date_edit.setDate(datetime.now().date())
                    self.service_entries[header] = date_edit
                    unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                    unknown_check.stateChanged.connect(lambda state, de=date_edit: de.setEnabled(state == Qt.Unchecked))
                    date_layout.addWidget(date_edit)
                    date_layout.addWidget(unknown_check)
                    self.service_entries[f"{header}_check"] = unknown_check
                    self.service_layout.addRow(label, date_layout)
                    continue
                elif header == TRANSLATIONS["description"]:
                    entry = QTextEdit()
                    entry.setMaximumHeight(75)
                    entry.setAcceptRichText(False)
                    self.service_entries[header] = entry
                elif param_type == "ComboBox" and combobox_file:
                    combo = QComboBox()
                    items = self.load_json_data(combobox_file, [])
                    combo.addItems([item["name"] for item in items])
                    combo.setEditable(True)
                    self.service_entries[header] = combo
                elif param_type == "Tarih":
                    date_layout = QHBoxLayout()
                    date_edit = QDateEdit()
                    date_edit.setCalendarPopup(True)
                    date_edit.setDisplayFormat("dd.MM.yyyy")
                    date_edit.setDate(datetime.now().date())
                    self.service_entries[header] = date_edit
                    unknown_check = QCheckBox(TRANSLATIONS["unknown"])
                    unknown_check.stateChanged.connect(lambda state, de=date_edit: de.setEnabled(state == Qt.Unchecked))
                    date_layout.addWidget(date_edit)
                    date_layout.addWidget(unknown_check)
                    self.service_entries[f"{header}_check"] = unknown_check
                    self.service_layout.addRow(label, date_layout)
                    continue
                else:
                    entry = QLineEdit()
                    self.service_entries[header] = entry
            self.service_layout.addRow(label, self.service_entries[header])
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
        visible_headers = [h for h in self.get_column_headers() if h != TRANSLATIONS["photo"]] + ["Son Güncelleme"]
        self.table.setColumnCount(len(visible_headers))
        self.table.setHorizontalHeaderLabels(visible_headers)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.itemDoubleClicked.connect(self.show_details)
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
        tools_menu = QMenu(self)
        tools_menu.addAction(qta.icon('fa5s.sliders-h', color='#D32F2F'), TRANSLATIONS["param_management"], self.manage_parameters)
        tools_menu.addAction(qta.icon('fa5s.database', color='#D32F2F'), TRANSLATIONS["backup_operations"], self.manage_backups)
        tools_menu.addAction(qta.icon('fa5s.chart-pie', color='#D32F2F'), TRANSLATIONS["data_analysis"], self.show_data_analysis)
        tools_menu.addAction(qta.icon('fa5s.list-alt', color='#D32F2F'), TRANSLATIONS["combobox_management"], self.manage_comboboxes)
        self.tools_button.setMenu(tools_menu)
        button_layout.addWidget(self.tools_button)

        self.close_button = QPushButton(TRANSLATIONS["close_item"])
        self.close_button.setIcon(qta.icon('fa5s.times', color='#D32F2F'))
        self.close_button.clicked.connect(self.close_application)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def toggle_donor(self, entry, state):
        entry.setEnabled(state == Qt.Unchecked)
        if state == Qt.Checked:
            entry.clear()

    def toggle_photo(self, entry, state):
        entry.setEnabled(state == Qt.Unchecked)
        if state == Qt.Checked:
            entry.clear()

    def select_photo(self, entry):
        file_name, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if file_name:
            entry.setText(file_name)
            logging.info(f"InventoryApp'da 'Demirbaş Fotoğrafı' için seçilen dosya: {file_name}")

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
        visible_headers = [h for h in self.get_column_headers() if h != TRANSLATIONS["photo"]] + ["Son Güncelleme"]
        self.archive_table.setColumnCount(len(visible_headers))
        self.archive_table.setHorizontalHeaderLabels(visible_headers)
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
            "startup_group": "Genel",
            "combobox_files": {
                TRANSLATIONS["group_name"]: GROUPS_FILE,
                TRANSLATIONS["region"]: REGIONS_FILE,
                TRANSLATIONS["floor"]: FLOORS_FILE
            }
        }
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                loaded_config = json.load(f)
                self.config = {**default_config, **loaded_config}
                if "combobox_files" not in self.config or not self.config["combobox_files"]:
                    self.config["combobox_files"] = default_config["combobox_files"]
        else:
            self.config = default_config.copy()
        self.save_config()

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
        if self.config["startup_group"] != "Son Kullanılan" and hasattr(self, 'card_entries'):
            self.card_entries[TRANSLATIONS["group_name"]].setCurrentText(self.config["startup_group"])
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
        self.save_config()

    def update_default_group(self):
        self.config["default_group"] = self.default_group_combo.currentText()
        if hasattr(self, 'card_entries'):
            self.card_entries[TRANSLATIONS["group_name"]].setCurrentText(self.config["default_group"])
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
                "startup_group": "Genel",
                "combobox_files": {
                    TRANSLATIONS["group_name"]: GROUPS_FILE,
                    TRANSLATIONS["region"]: REGIONS_FILE,
                    TRANSLATIONS["floor"]: FLOORS_FILE
                }
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
        headers = self.get_column_headers()  # Dinamik headers alımı
        visible_headers = [h for h in headers if h != TRANSLATIONS["photo"]] + ["Son Güncelleme"]
        self.table.setColumnCount(len(visible_headers))
        self.table.setHorizontalHeaderLabels(visible_headers)

        cursor = self.conn.cursor()
        cursor.execute("SELECT id, data, timestamp FROM inventory")
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))

        for row_idx, (row_id, data_json, timestamp) in enumerate(rows):
            data = json.loads(data_json)
            # headers ile data uzunluğunu eşitle
            if len(data) < len(headers):
                data.extend([""] * (len(headers) - len(data)))
            elif len(data) > len(headers):
                data = data[:len(headers)]

            for col_idx, header in enumerate(visible_headers):
                if header == "Son Güncelleme":
                    item = QTableWidgetItem(timestamp)
                else:
                    header_idx = headers.index(header) if header in headers else -1
                    value = data[header_idx] if header_idx != -1 else ""
                    item = QTableWidgetItem(value)
                item.setData(Qt.UserRole, row_id)  # row_id sakla
                self.table.setItem(row_idx, col_idx, item)

        self.table.resizeColumnsToContents()
        logging.info(f"load_data_from_db: Tablo {len(rows)} satırla güncellendi, headers={visible_headers}")

    def load_archive_from_db(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT id, data, timestamp FROM archive")
        rows = cursor.fetchall()
        headers = self.get_column_headers()
        visible_headers = [h for h in headers if h != TRANSLATIONS["photo"]]
        self.archive_table.setRowCount(len(rows))
        self.archive_table.setColumnCount(len(visible_headers) + 1)
        self.archive_table.setHorizontalHeaderLabels(visible_headers + ["Son Güncelleme"])
        for row_idx, (row_id, row_data, timestamp) in enumerate(rows):
            data = json.loads(row_data)
            if len(data) < len(headers):
                data.extend([""] * (len(headers) - len(data)))
            for col, value in enumerate([data[headers.index(h)] for h in visible_headers]):
                self.archive_table.setItem(row_idx, col, QTableWidgetItem(str(value)))
            self.archive_table.setItem(row_idx, len(visible_headers), QTableWidgetItem(timestamp))
            if self.archive_table.item(row_idx, 0):
                self.archive_table.item(row_idx, 0).setData(Qt.UserRole, row_id)

    def add_item(self):
        headers = self.get_column_headers()
        data = []
        for header in headers:
            if header in self.card_entries:
                if header == "Edinim Tarihi" or header == TRANSLATIONS["warranty_period"]:
                    if f"{header}_check" in self.card_entries and self.card_entries[f"{header}_check"].isChecked():
                        value = TRANSLATIONS["unknown"]
                    else:
                        value = self.card_entries[header].date().toString("dd.MM.yyyy")
                elif header == TRANSLATIONS["photo"]:
                    if f"{header}_check" in self.card_entries and self.card_entries[f"{header}_check"].isChecked():
                        value = ""
                    else:
                        value = self.card_entries[header].text()  # Doğru QLineEdit'ten alınır
                else:
                    value = self.get_widget_value(self.card_entries[header])
            elif header in self.invoice_entries:
                if header == "Bağışçı" and f"{header}_check" in self.invoice_entries and self.invoice_entries[f"{header}_check"].isChecked():
                    value = ""
                else:
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
            logging.info(f"add_item: '{header}' için toplanan veri: {value}")

        if len(data) != len(headers):
            logging.error(f"Data uzunluğu ({len(data)}) ile headers uzunluğu ({len(headers)}) uyuşmuyor!")
            QMessageBox.critical(self, "Hata", "Veri ve başlık sayısı uyuşmuyor. Lütfen geliştirici ile iletişime geçin.")
            return

        group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
        item_name_idx = headers.index(TRANSLATIONS["item_name"]) if TRANSLATIONS["item_name"] in headers else -1
        region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
        floor_idx = headers.index(TRANSLATIONS["floor"]) if TRANSLATIONS["floor"] in headers else -1
        code_idx = headers.index("Demirbaş Kodu") if "Demirbaş Kodu" in headers else -1

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
                           ("Demirbaş Kodu", 0, TRANSLATIONS["card_info"]))
            self.conn.commit()
            headers.insert(0, "Demirbaş Kodu")
            data.insert(0, inventory_code)
            self.setup_inventory_tab()

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(data), timestamp))
        self.conn.commit()
        self.load_data_from_db()
        QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_added"] + f"\nDemirbaş Kodu: {inventory_code}")
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
        cursor = self.conn.cursor()
        row_id = self.table.item(selected, 0).data(Qt.UserRole)
        dialog = EditDialog(self, [self.table.item(selected, 0)], headers)  # row_id için sadece ilk sütunu gönderiyoruz
        if dialog.exec_():
            updated_data = dialog.get_data()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
            region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
            floor_idx = headers.index(TRANSLATIONS["floor"]) if TRANSLATIONS["floor"] in headers else -1
            code_idx = headers.index("Demirbaş Kodu") if "Demirbaş Kodu" in headers else -1

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
        if selected < 0:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return

        headers = self.get_column_headers()  # Dinamik headers alımı
        cursor = self.conn.cursor()
        row_id = self.table.item(selected, 0).data(Qt.UserRole)
        cursor.execute("SELECT data FROM inventory WHERE id = ?", (row_id,))
        full_data = json.loads(cursor.fetchone()[0])

        # full_data'nın headers ile uyumlu olduğundan emin olalım
        if len(full_data) < len(headers):
            full_data.extend([""] * (len(headers) - len(full_data)))
        elif len(full_data) > len(headers):
            full_data = full_data[:len(headers)]

        logging.info(f"duplicate_item: headers={headers}")
        logging.info(f"duplicate_item: original full_data={full_data}")

        # Yeni demirbaş kodu oluştur
        group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
        region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
        floor_idx = headers.index(TRANSLATIONS["floor"]) if TRANSLATIONS["floor"] in headers else -1
        code_idx = headers.index("Demirbaş Kodu") if "Demirbaş Kodu" in headers else -1

        if group_name_idx != -1 and region_idx != -1 and floor_idx != -1:
            group_name = full_data[group_name_idx]
            region_name = full_data[region_idx]
            floor_name = full_data[floor_idx]
            new_code = self.generate_inventory_code(group_name, region_name, floor_name)
            if code_idx != -1:
                full_data[code_idx] = new_code

        # Yeni timestamp ile kopyayı ekle
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(full_data), timestamp))
        self.conn.commit()
        self.load_data_from_db()

        logging.info(f"duplicate_item: duplicated data={full_data}")
        QMessageBox.information(self, "Başarılı", f"Öğe çoğaltıldı! Yeni Demirbaş Kodu: {new_code}")

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

            cursor = self.conn.cursor()
            row_id = self.table.item(selected, 0).data(Qt.UserRole)
            cursor.execute("SELECT data FROM inventory WHERE id = ?", (row_id,))
            full_data = json.loads(cursor.fetchone()[0])
            data = full_data if len(full_data) == len(headers) else full_data + [""] * (len(headers) - len(full_data))

            dialog = QDialog(self)
            dialog.setWindowTitle(TRANSLATIONS["details_title"])
            dialog.setMinimumSize(800, 600)
            layout = QVBoxLayout(dialog)

            # Demirbaş Fotoğrafını en üste ekle
            photo_idx = headers.index(TRANSLATIONS["photo"]) if TRANSLATIONS["photo"] in headers else -1
            if photo_idx != -1 and data[photo_idx]:
                photo_label = QLabel("Demirbaş Fotoğrafı:")
                photo_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                photo_widget = QLabel()
                pixmap = QPixmap(data[photo_idx])
                if not pixmap.isNull():
                    pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio)
                    photo_widget.setPixmap(pixmap)
                else:
                    photo_widget.setText("Fotoğraf yüklenemedi")
                layout.addWidget(photo_label)
                layout.addWidget(photo_widget)
                layout.addSpacing(10)

            # Diğer alanları tablarda göster
            tabs = QTabWidget()
            card_tab = QWidget()
            invoice_tab = QWidget()
            service_tab = QWidget()

            card_layout = QFormLayout(card_tab)
            invoice_layout = QFormLayout(invoice_tab)
            service_layout = QFormLayout(service_tab)

            cursor.execute("SELECT column_name, section FROM metadata ORDER BY column_order")
            metadata = cursor.fetchall()
            if not metadata:
                logging.warning("Metadata tablosu boş, varsayılan bölüm kullanılıyor.")
                metadata = [(header, TRANSLATIONS["card_info"]) for header in headers]

            card_count = 0
            invoice_count = 0
            service_count = 0

            for i, (header, value) in enumerate(zip(headers, data)):
                if header == TRANSLATIONS["photo"]:  # Fotoğrafı zaten üstte gösterdik, atla
                    continue
                section = next((m[1] for m in metadata if m[0] == header), TRANSLATIONS["card_info"])
                label = QLabel(f"{header}:")
                label.setStyleSheet("font-weight: bold; font-size: 14px;")

                if header in ["Özellikler", TRANSLATIONS["description"]]:
                    value_widget = QTextEdit(value)
                    value_widget.setReadOnly(True)
                    value_widget.setStyleSheet("font-size: 14px; margin-left: 10px; padding: 5px; border: 1px solid #ccc;")
                    value_widget.setMinimumHeight(100 if header == "Özellikler" else 75)
                    value_widget.setWordWrapMode(QTextOption.WordWrap)
                    value_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
                else:
                    value_widget = QLabel(value if value else "Bilgi Yok")
                    value_widget.setStyleSheet("font-size: 14px; margin-left: 10px;")
                    value_widget.setWordWrap(True)

                if section == TRANSLATIONS["card_info"]:
                    card_layout.addRow(label, value_widget)
                    card_count += 1
                elif section == TRANSLATIONS["invoice_info"]:
                    invoice_layout.addRow(label, value_widget)
                    invoice_count += 1
                elif section == TRANSLATIONS["service_info"]:
                    service_layout.addRow(label, value_widget)
                    service_count += 1

            tabs.addTab(card_tab, f"{TRANSLATIONS['card_info']} ({card_count})")
            tabs.addTab(invoice_tab, f"{TRANSLATIONS['invoice_info']} ({invoice_count})")
            tabs.addTab(service_tab, f"{TRANSLATIONS['service_info']} ({service_count})")
            layout.addWidget(tabs)

            code_idx = headers.index("Demirbaş Kodu") if "Demirbaş Kodu" in headers else -1
            if code_idx != -1 and code_idx < len(data):
                code = data[code_idx]
                decoded_info = self.decode_inventory_code(code)
                code_label = QLabel(f"Kod Çözümleme: {decoded_info}")
                code_label.setStyleSheet("font-weight: bold; color: #D32F2F; font-size: 14px; margin-top: 10px;")
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
                    if header != TRANSLATIONS["photo"]:
                        table_data.append([header, value])
                    elif value:
                        elements.append(Paragraph("Demirbaş Fotoğrafı:", styles['Heading2']))
                        elements.append(Image(value, width=5 * cm, height=5 * cm))
                        elements.append(Spacer(1, 0.5 * cm))

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
            cursor = self.conn.cursor()
            row_id = self.archive_table.item(selected, 0).data(Qt.UserRole)
            cursor.execute("SELECT data FROM archive WHERE id = ?", (row_id,))
            full_data = json.loads(cursor.fetchone()[0])
            data = full_data if len(full_data) == len(headers) else full_data + [""] * (len(headers) - len(full_data))

            dialog = QDialog(self)
            dialog.setWindowTitle(TRANSLATIONS["details_title"])
            layout = QVBoxLayout(dialog)
            detail_table = QTableWidget(len(headers), 2)
            detail_table.setHorizontalHeaderLabels(["Alan", "Değer"])
            detail_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
            for row, (header, value) in enumerate(zip(headers, data)):
                detail_table.setItem(row, 0, QTableWidgetItem(header))
                if header == TRANSLATIONS["photo"] and value:
                    pixmap = QPixmap(value)
                    label = QLabel()
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(100, 100, Qt.KeepAspectRatio)
                        label.setPixmap(pixmap)
                    else:
                        label.setText("Fotoğraf yüklenemedi")
                    detail_table.setCellWidget(row, 1, label)
                else:
                    detail_table.setItem(row, 1, QTableWidgetItem(value if value else "Bilgi Yok"))
            layout.addWidget(detail_table)
            close_button = QPushButton(TRANSLATIONS["close_item"])
            close_button.clicked.connect(dialog.accept)
            layout.addWidget(close_button)
            dialog.exec_()
        else:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])

    def restore_archive_item(self):
        selected = self.archive_table.currentRow()  # archive_table'dan seçim yapıldığı için düzeltildi
        if selected < 0:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return

        headers = self.get_column_headers()
        cursor = self.conn.cursor()
        row_id = self.archive_table.item(selected, 0).data(Qt.UserRole)  # Arşiv tablosundan row_id al
        cursor.execute("SELECT data FROM archive WHERE id = ?", (row_id,))
        full_data = json.loads(cursor.fetchone()[0])
        
        # full_data'nın headers ile uyumlu olduğundan emin olalım
        if len(full_data) < len(headers):
            full_data.extend([""] * (len(headers) - len(full_data)))
        elif len(full_data) > len(headers):
            full_data = full_data[:len(headers)]

        dialog = EditDialog(self, full_data, headers)  # row_data olarak full_data gönderiyoruz
        if dialog.exec_():
            updated_data = dialog.get_data()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(updated_data), timestamp))
            cursor.execute("DELETE FROM archive WHERE id = ?", (row_id,))
            self.conn.commit()
            self.load_data_from_db()
            self.load_archive_from_db()
            QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_restored"])

    def export_to_file(self):
        headers = self.get_column_headers()
        visible_headers = [h for h in headers if h != TRANSLATIONS["photo"]]
        data = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(len(visible_headers))]
            data.append(row_data)

        if not data:
            QMessageBox.warning(self, "Hata", "Dışa aktarılacak veri yok!")
            return

        file_format = self.config["export_format"]
        file_name, _ = QFileDialog.getSaveFileName(self, "Dosyayı Kaydet", "", file_format)
        if file_name:
            try:
                df = pd.DataFrame(data, columns=visible_headers)
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
                    self.conn.commit()

                for _, row in df.iterrows():
                    data = [str(row.get(header, "")) for header in headers]
                    if len(data) < len(headers):
                        data.extend([""] * (len(headers) - len(data)))
                    group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
                    region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
                    floor_idx = headers.index(TRANSLATIONS["floor"]) if TRANSLATIONS["floor"] in headers else -1
                    code_idx = headers.index("Demirbaş Kodu") if "Demirbaş Kodu" in headers else -1

                    if group_name_idx != -1 and region_idx != -1 and floor_idx != -1:
                        group_name = data[group_name_idx]
                        region_name = data[region_idx]
                        floor_name = data[floor_idx]
                        if code_idx != -1 and not data[code_idx]:
                            data[code_idx] = self.generate_inventory_code(group_name, region_name, floor_name)

                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
        visible_headers = [h for h in headers if h != TRANSLATIONS["photo"]]
        dialog = ColumnSelectionDialog(visible_headers, self)
        if dialog.exec_():
            selected_headers = dialog.get_selected_columns()
            if not selected_headers:
                QMessageBox.warning(self, "Hata", "En az bir sütun seçmelisiniz!")
                return

            file_name, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "", "PDF (*.pdf)")
            if file_name:
                try:
                    doc = SimpleDocTemplate(file_name, pagesize=landscape(A4))
                    elements = []
                    styles = getSampleStyleSheet()

                    # Kurum başlığını şekillendir
                    title_style = ParagraphStyle(
                        'TitleStyle',
                        parent=styles['Heading1'],
                        fontName=self.default_font,
                        fontSize=16,
                        textColor=colors.darkred,
                        alignment=1,
                        spaceAfter=10,
                        borderWidth=1,
                        borderColor=colors.black,
                        borderPadding=5
                    )
                    title = Paragraph(TRANSLATIONS["title"], title_style)
                    elements.append(title)

                    # Kurum adresleri ve oluşturulma tarihi
                    address_style = ParagraphStyle(
                        'AddressStyle',
                        parent=styles['Normal'],
                        fontName=self.default_font,
                        fontSize=10,
                        textColor=colors.black,
                        alignment=1,
                        spaceAfter=5
                    )
                    address_text = (
                        "Florya, Şenlikköy Mh. Orman Sk. No:39/1 Florya Bakırköy/İstanbul<br/>"
                        "E-posta: bilgi@gsyardimlasmavakfi.org | Telefon: (0212) 574 52 55"
                    )
                    address = Paragraph(address_text, address_style)
                    elements.append(address)

                    date_style = ParagraphStyle(
                        'DateStyle',
                        parent=styles['Normal'],
                        fontName=self.default_font,
                        fontSize=9,
                        textColor=colors.grey,
                        alignment=1,
                        spaceAfter=10
                    )
                    creation_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                    date_text = f"Oluşturulma Tarihi: {creation_date}"
                    date = Paragraph(date_text, date_style)
                    elements.append(date)

                    # Logo ekle (varsa)
                    if os.path.exists(LOGO_FILE):
                        logo = Image(LOGO_FILE, width=2 * cm, height=2 * cm)
                        logo.hAlign = 'CENTER'
                        elements.append(logo)
                        elements.append(Spacer(1, 0.5 * cm))

                    # Tüm veriyi tablo için hazırla, "No" yerine "Fotoğraf" sütunu
                    table_data = [["Fotoğraf"] + selected_headers]  # Başlık satırı
                    photo_idx = headers.index(TRANSLATIONS["photo"]) if TRANSLATIONS["photo"] in headers else -1
                    
                    cursor = self.conn.cursor()
                    cursor.execute("SELECT data FROM inventory")
                    rows = cursor.fetchall()

                    for row_idx, row in enumerate(rows):
                        data = json.loads(row[0])
                        if len(data) < len(headers):
                            data.extend([""] * (len(headers) - len(data)))

                        row_data = []
                        # Fotoğraf sütunu
                        if photo_idx != -1 and data[photo_idx] and os.path.exists(data[photo_idx]):
                            photo = Image(data[photo_idx], width=1 * cm, height=1 * cm)  # Küçük fotoğraf
                            row_data.append(photo)
                        else:
                            row_data.append("Foto Yok")

                        # Diğer sütunlar
                        for header in selected_headers:
                            col_idx = headers.index(header)
                            row_data.append(data[col_idx] if col_idx < len(data) else "")
                        table_data.append(row_data)

                    # Tablo stilini tanımla
                    table_style = TableStyle([
                        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Fotoğraflar için ortala
                        ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                        ('FONTSIZE', (0, 0), (-1, 0), 7),
                        ('FONTSIZE', (0, 1), (-1, -1), 6),
                        ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                        ('TOPPADDING', (0, 0), (-1, -1), 2),
                        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('LEFTPADDING', (0, 0), (-1, -1), 2),
                        ('RIGHTPADDING', (0, 0), (-1, -1), 2),
                        ('WORDWRAP', (1, 0), (-1, -1), True),  # Fotoğraf sütunu hariç kaydırma
                    ])

                    # Sütun genişliklerini içeriğe göre dinamik ayarla
                    page_width = landscape(A4)[0] - 2 * cm  # Sayfanın kullanılabilir genişliği
                    num_cols = len(selected_headers) + 1  # "Fotoğraf" sütunu dahil
                    base_col_width = page_width / num_cols

                    # Her sütunun maksimum içerik uzunluğunu hesapla
                    col_max_lengths = [len(str(table_data[0][i])) for i in range(num_cols)]  # Başlık uzunlukları
                    for row in table_data[1:]:
                        for i, cell in enumerate(row):
                            if i == 0 and isinstance(cell, Image):
                                col_max_lengths[i] = max(col_max_lengths[i], 10)  # Fotoğraf için sabit bir değer
                            else:
                                col_max_lengths[i] = max(col_max_lengths[i], len(str(cell)))

                    # Toplam uzunluğa göre sütun genişliklerini oranla
                    total_length = sum(col_max_lengths)
                    col_widths = []
                    for i, length in enumerate(col_max_lengths):
                        if total_length > 0:
                            width = (length / total_length) * page_width
                            if i == 0:  # Fotoğraf sütunu için sabit genişlik
                                col_widths.append(1.2 * cm)  # Fotoğraflar için biraz daha geniş
                            else:
                                col_widths.append(max(width, base_col_width * 0.5))  # Minimum genişlik sınırı
                        else:
                            col_widths.append(base_col_width)

                    # Tabloyu oluştur
                    table = Table(table_data, colWidths=col_widths)
                    table.setStyle(table_style)

                    # Tabloyu ekle
                    elements.append(table)

                    # PDF'i oluştur
                    doc.build(elements)
                    QMessageBox.information(self, "Başarılı", TRANSLATIONS["pdf_generated"])
                    logging.info(f"PDF raporu {file_name} dosyasına oluşturuldu.")
                except Exception as e:
                    QMessageBox.critical(self, "Hata", f"PDF oluşturma başarısız: {str(e)}")
                    logging.error(f"PDF rapor oluşturma hatası: {str(e)}")
                    
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
        group_idx = self.get_column_headers().index(TRANSLATIONS["group_name"])
        for row in range(self.table.rowCount()):
            group_item = self.table.item(row, group_idx)
            group = group_item.text() if group_item else ""
            self.table.setRowHidden(row, filter_group != "Tümü" and group != filter_group)

    def manage_parameters(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["param_management"])
        layout = QVBoxLayout(dialog)

        self.param_list = QListWidget()
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name FROM metadata ORDER BY column_order")
        for row in cursor.fetchall():
            self.param_list.addItem(row[0])
        layout.addWidget(self.param_list)

        button_layout = QHBoxLayout()
        add_button = QPushButton(TRANSLATIONS["add_parameter"])
        add_button.clicked.connect(self.add_parameter)
        button_layout.addWidget(add_button)

        edit_button = QPushButton(TRANSLATIONS["edit_parameter"])
        edit_button.clicked.connect(self.edit_parameter)
        button_layout.addWidget(edit_button)

        delete_button = QPushButton(TRANSLATIONS["delete_parameter"])
        delete_button.clicked.connect(self.delete_parameter)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)
        dialog.exec_()

    def add_parameter(self):
        dialog = AddParameterDialog(self)
        if dialog.exec_():
            name, section, param_type, combobox_file = dialog.get_data()
            if name and name not in self.get_column_headers():
                cursor = self.conn.cursor()
                cursor.execute("SELECT MAX(column_order) FROM metadata")
                max_order = cursor.fetchone()[0] or 0
                cursor.execute("INSERT INTO metadata (column_name, column_order, section, type, combobox_file) VALUES (?, ?, ?, ?, ?)",
                               (name, max_order + 1, section, param_type, combobox_file))
                self.conn.commit()
                self.param_list.addItem(name)
                self.setup_inventory_tab()
                self.update_comboboxes()
                QMessageBox.information(self, "Başarılı", f"'{name}' parametresi eklendi!")

    def edit_parameter(self):
        selected = self.param_list.currentItem()
        if selected:
            old_name = selected.text()
            dialog = EditParameterDialog(self, old_name)
            if dialog.exec_():
                new_name, section, param_type, combobox_file = dialog.get_data()
                if new_name:
                    cursor = self.conn.cursor()
                    cursor.execute("UPDATE metadata SET column_name = ?, section = ?, type = ?, combobox_file = ? WHERE column_name = ?",
                                   (new_name, section, param_type, combobox_file, old_name))
                    self.conn.commit()
                    selected.setText(new_name)
                    self.setup_inventory_tab()  # Tabloyu sıfırdan oluştur
                    self.load_data_from_db()   # Verileri yeni sırayla yükle
                    self.update_comboboxes()
                    QMessageBox.information(self, "Başarılı", f"'{old_name}' parametresi '{new_name}' olarak güncellendi!")
        else:
            QMessageBox.warning(self, "Hata", "Lütfen bir parametre seçin!")

    def delete_parameter(self):
        selected = self.param_list.currentItem()
        if selected:
            name = selected.text()
            if QMessageBox.question(self, "Onay", f"'{name}' parametresini silmek istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                cursor = self.conn.cursor()
                cursor.execute("DELETE FROM metadata WHERE column_name = ?", (name,))
                self.conn.commit()
                self.param_list.takeItem(self.param_list.row(selected))
                self.setup_inventory_tab()
                QMessageBox.information(self, "Başarılı", f"'{name}' parametresi silindi!")
        else:
            QMessageBox.warning(self, "Hata", "Lütfen bir parametre seçin!")

    def manage_backups(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["backup_operations"])
        layout = QVBoxLayout(dialog)

        backup_button = QPushButton(TRANSLATIONS["manual_backup"])
        backup_button.clicked.connect(self.manual_backup)
        layout.addWidget(backup_button)

        dialog.exec_()

    def manual_backup(self):
        self.auto_backup()
        QMessageBox.information(self, "Başarılı", TRANSLATIONS["db_backed_up"])

    def auto_backup(self):
        backup_dir = self.config["backup_path"]
        os.makedirs(backup_dir, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(backup_dir, f"inventory_backup_{timestamp}.db")
        shutil.copy2(DB_FILE, backup_file)
        logging.info(f"Veritabanı yedeklendi: {backup_file}")

        now = time.time()
        cutoff = now - (self.config["backup_retention"] * 86400)
        for old_backup in glob.glob(os.path.join(backup_dir, "inventory_backup_*.db")):
            if os.path.getctime(old_backup) < cutoff:
                os.remove(old_backup)
                logging.info(f"Eski yedek silindi: {old_backup}")

    def show_data_analysis(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["analysis_title"])
        dialog.setMinimumSize(800, 600)
        layout = QVBoxLayout(dialog)

        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM inventory")
        rows = cursor.fetchall()
        total_records = len(rows)
        layout.addWidget(QLabel(TRANSLATIONS["total_records"].format(total_records)))

        group_counts = {}
        status_counts = {}
        region_counts = {}
        brand_counts = {}
        warranty_status = {"Geçerli": 0, "Süresi Dolmuş": 0, "Bilinmeyen": 0}
        headers = self.get_column_headers()
        group_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
        status_idx = headers.index(TRANSLATIONS["status"]) if TRANSLATIONS["status"] in headers else -1
        region_idx = headers.index(TRANSLATIONS["region"]) if TRANSLATIONS["region"] in headers else -1
        brand_idx = headers.index(TRANSLATIONS["brand"]) if TRANSLATIONS["brand"] in headers else -1
        warranty_idx = headers.index(TRANSLATIONS["warranty_period"]) if TRANSLATIONS["warranty_period"] in headers else -1

        current_date = datetime.now()
        for row in rows:
            data = json.loads(row[0])
            if group_idx != -1 and group_idx < len(data):
                group = data[group_idx] or "Bilinmeyen"
                group_counts[group] = group_counts.get(group, 0) + 1
            if status_idx != -1 and status_idx < len(data):
                status = data[status_idx] or "Bilinmeyen"
                status_counts[status] = status_counts.get(status, 0) + 1
            if region_idx != -1 and region_idx < len(data):
                region = data[region_idx] or "Bilinmeyen"
                region_counts[region] = region_counts.get(region, 0) + 1
            if brand_idx != -1 and brand_idx < len(data):
                brand = data[brand_idx] or "Bilinmeyen"
                brand_counts[brand] = brand_counts.get(brand, 0) + 1
            if warranty_idx != -1 and warranty_idx < len(data):
                warranty = data[warranty_idx]
                if warranty == TRANSLATIONS["unknown"]:
                    warranty_status["Bilinmeyen"] += 1
                else:
                    try:
                        warranty_date = datetime.strptime(warranty, "%d.%m.%Y")
                        if warranty_date > current_date:
                            warranty_status["Geçerli"] += 1
                        else:
                            warranty_status["Süresi Dolmuş"] += 1
                    except ValueError:
                        warranty_status["Bilinmeyen"] += 1

        tabs = QTabWidget()

        # Grup Dağılımı
        group_tab = QWidget()
        group_layout = QVBoxLayout(group_tab)
        group_layout.addWidget(QLabel(TRANSLATIONS["group_distribution"]))
        fig1, ax1 = plt.subplots(figsize=(6, 4))
        ax1.pie(group_counts.values(), labels=group_counts.keys(), autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
        ax1.axis('equal')
        ax1.set_title(TRANSLATIONS["group_distribution"], fontsize=12)
        canvas1 = FigureCanvas(fig1)
        cursor1 = mplcursors.cursor(ax1, hover=True)
        cursor1.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[0]:.1f}%"))
        group_layout.addWidget(canvas1)
        tabs.addTab(group_tab, TRANSLATIONS["group_distribution"])

        # Durum Dağılımı
        status_tab = QWidget()
        status_layout = QVBoxLayout(status_tab)
        status_layout.addWidget(QLabel(TRANSLATIONS["status_distribution"]))
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        bars = ax2.bar(status_counts.keys(), status_counts.values(), color='skyblue')
        ax2.set_ylabel("Kayıt Sayısı", fontsize=10)
        ax2.set_title(TRANSLATIONS["status_distribution"], fontsize=12)
        plt.xticks(rotation=45, ha='right', fontsize=8)
        canvas2 = FigureCanvas(fig2)
        cursor2 = mplcursors.cursor(bars, hover=True)
        cursor2.connect("add", lambda sel: sel.annotation.set_text(f"{int(sel.target[1])}"))
        status_layout.addWidget(canvas2)
        tabs.addTab(status_tab, TRANSLATIONS["status_distribution"])

        # Bölge Dağılımı
        region_tab = QWidget()
        region_layout = QVBoxLayout(region_tab)
        region_layout.addWidget(QLabel(TRANSLATIONS["region_distribution"]))
        fig3, ax3 = plt.subplots(figsize=(6, 4))
        ax3.pie(region_counts.values(), labels=region_counts.keys(), autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
        ax3.axis('equal')
        ax3.set_title(TRANSLATIONS["region_distribution"], fontsize=12)
        canvas3 = FigureCanvas(fig3)
        cursor3 = mplcursors.cursor(ax3, hover=True)
        cursor3.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[0]:.1f}%"))
        region_layout.addWidget(canvas3)
        tabs.addTab(region_tab, TRANSLATIONS["region_distribution"])

        # Marka Dağılımı
        brand_tab = QWidget()
        brand_layout = QVBoxLayout(brand_tab)
        brand_layout.addWidget(QLabel(TRANSLATIONS["brand_distribution"]))
        fig4, ax4 = plt.subplots(figsize=(6, 4))
        ax4.pie(brand_counts.values(), labels=brand_counts.keys(), autopct='%1.1f%%', startangle=90, textprops={'fontsize': 10})
        ax4.axis('equal')
        ax4.set_title(TRANSLATIONS["brand_distribution"], fontsize=12)
        canvas4 = FigureCanvas(fig4)
        cursor4 = mplcursors.cursor(ax4, hover=True)
        cursor4.connect("add", lambda sel: sel.annotation.set_text(f"{sel.target[0]:.1f}%"))
        brand_layout.addWidget(canvas4)
        tabs.addTab(brand_tab, TRANSLATIONS["brand_distribution"])

        # Garanti Durumu
        warranty_tab = QWidget()
        warranty_layout = QVBoxLayout(warranty_tab)
        warranty_layout.addWidget(QLabel(TRANSLATIONS["warranty_status"]))
        fig5, ax5 = plt.subplots(figsize=(6, 4))
        bars5 = ax5.bar(warranty_status.keys(), warranty_status.values(), color=['green', 'red', 'gray'])
        ax5.set_ylabel("Kayıt Sayısı", fontsize=10)
        ax5.set_title(TRANSLATIONS["warranty_status"], fontsize=12)
        canvas5 = FigureCanvas(fig5)
        cursor5 = mplcursors.cursor(bars5, hover=True)
        cursor5.connect("add", lambda sel: sel.annotation.set_text(f"{int(sel.target[1])}"))
        warranty_layout.addWidget(canvas5)
        tabs.addTab(warranty_tab, TRANSLATIONS["warranty_status"])

        layout.addWidget(tabs)

        button_layout = QHBoxLayout()
        export_charts_button = QPushButton(TRANSLATIONS["export_charts"])
        export_charts_button.setIcon(qta.icon('fa5s.image', color='#FFC107'))
        export_charts_button.clicked.connect(lambda: self.export_charts([fig1, fig2, fig3, fig4, fig5]))
        button_layout.addWidget(export_charts_button)

        export_data_button = QPushButton(TRANSLATIONS["export_analysis_data"])
        export_data_button.setIcon(qta.icon('fa5s.file-excel', color='#FFC107'))
        export_data_button.clicked.connect(lambda: self.export_analysis_data(group_counts, status_counts, region_counts, brand_counts, warranty_status))
        button_layout.addWidget(export_data_button)

        close_button = QPushButton(TRANSLATIONS["close_item"])
        close_button.setIcon(qta.icon('fa5s.times', color='#D32F2F'))
        close_button.clicked.connect(dialog.accept)
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)
        dialog.exec_()

    def export_charts(self, figures):
        folder = QFileDialog.getExistingDirectory(self, "Grafikleri Kaydet", "")
        if folder:
            try:
                for i, fig in enumerate(figures, 1):
                    file_name = os.path.join(folder, f"chart_{i}.png")
                    fig.savefig(file_name, dpi=300, bbox_inches='tight')
                    logging.info(f"Grafik {file_name} olarak kaydedildi.")
                QMessageBox.information(self, "Başarılı", "Grafikler PNG olarak kaydedildi!")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Grafik dışa aktarma başarısız: {str(e)}")
                logging.error(f"Grafik dışa aktarma hatası: {str(e)}")

    def export_analysis_data(self, group_counts, status_counts, region_counts, brand_counts, warranty_status):
        file_name, _ = QFileDialog.getSaveFileName(self, "Analiz Verilerini Kaydet", "", "Excel (*.xlsx)")
        if file_name:
            try:
                data = {
                    TRANSLATIONS["group_distribution"]: pd.Series(group_counts),
                    TRANSLATIONS["status_distribution"]: pd.Series(status_counts),
                    TRANSLATIONS["region_distribution"]: pd.Series(region_counts),
                    TRANSLATIONS["brand_distribution"]: pd.Series(brand_counts),
                    TRANSLATIONS["warranty_status"]: pd.Series(warranty_status)
                }
                df = pd.DataFrame(data)
                df.to_excel(file_name, index_label="Kategori")
                QMessageBox.information(self, "Başarılı", "Analiz verileri Excel'e aktarıldı!")
                logging.info(f"Analiz verileri {file_name} dosyasına aktarıldı.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Analiz verileri dışa aktarma başarısız: {str(e)}")
                logging.error(f"Analiz verileri dışa aktarma hatası: {str(e)}")

    def manage_comboboxes(self):
        menu = QMenu(self)
        groups_action = menu.addAction(qta.icon('fa5s.list', color='#D32F2F'), "Demirbaş Cinslerini Düzenle")
        regions_action = menu.addAction(qta.icon('fa5s.map-marker-alt', color='#D32F2F'), "Lokasyonları Düzenle")
        floors_action = menu.addAction(qta.icon('fa5s.building', color='#D32F2F'), "Katları Düzenle")
        new_param_action = menu.addAction(qta.icon('fa5s.plus-circle', color='#D32F2F'), TRANSLATIONS["new_combobox_param"])

        groups_action.triggered.connect(lambda: self.edit_combobox("Demirbaş Cinsleri", self.groups, GROUPS_FILE))
        regions_action.triggered.connect(lambda: self.edit_combobox("Lokasyonlar", self.regions, REGIONS_FILE))
        floors_action.triggered.connect(lambda: self.edit_combobox("Katlar", self.floors, FLOORS_FILE))
        new_param_action.triggered.connect(self.add_new_combobox_param)

        menu.exec_(QCursor.pos())

    def edit_combobox(self, title, items, file_path):
        dialog = ComboBoxEditDialog(self, title, items, file_path)
        dialog.exec_()

    def add_new_combobox_param(self):
        dialog = AddParameterDialog(self)
        dialog.type_combo.setCurrentText("ComboBox")
        dialog.file_entry.setEnabled(True)
        if dialog.exec_():
            name, section, param_type, combobox_file = dialog.get_data()
            if name and combobox_file and name not in self.get_column_headers():
                if not os.path.exists(combobox_file):
                    default_data = [{"name": "Varsayılan", "code": "DEF"}]
                    self.save_json_data(combobox_file, default_data)
                cursor = self.conn.cursor()
                cursor.execute("SELECT MAX(column_order) FROM metadata")
                max_order = cursor.fetchone()[0] or 0
                cursor.execute("INSERT INTO metadata (column_name, column_order, section, type, combobox_file) VALUES (?, ?, ?, ?, ?)",
                               (name, max_order + 1, section, param_type, combobox_file))
                self.conn.commit()
                self.config["combobox_files"][name] = combobox_file
                self.save_config()
                self.setup_inventory_tab()
                self.update_comboboxes()
                QMessageBox.information(self, "Başarılı", f"'{name}' ComboBox parametresi eklendi!")

    def save_current_form(self):
        logging.info("Form otomatik kaydedildi.")

    def close_application(self):
        self.conn.close()
        self.close()

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
                            column_name TEXT UNIQUE,
                            column_order INTEGER,
                            section TEXT,
                            type TEXT DEFAULT 'Metin',
                            combobox_file TEXT)''')

        default_metadata = [
            ("Demirbaş Kodu", 0, TRANSLATIONS["card_info"], "Metin", None),
            (TRANSLATIONS["group_name"], 1, TRANSLATIONS["card_info"], "ComboBox", GROUPS_FILE),
            (TRANSLATIONS["item_name"], 2, TRANSLATIONS["card_info"], "Metin", None),
            (TRANSLATIONS["region"], 3, TRANSLATIONS["card_info"], "ComboBox", REGIONS_FILE),
            (TRANSLATIONS["floor"], 4, TRANSLATIONS["card_info"], "ComboBox", FLOORS_FILE),
            (TRANSLATIONS["quantity"], 5, TRANSLATIONS["card_info"], "Metin", None),
            (TRANSLATIONS["photo"], 6, TRANSLATIONS["card_info"], "Metin", None),
            (TRANSLATIONS["brand"], 7, TRANSLATIONS["card_info"], "Metin", None),
            (TRANSLATIONS["model"], 8, TRANSLATIONS["card_info"], "Metin", None),
            ("Edinim Tarihi", 9, TRANSLATIONS["card_info"], "Tarih", None),
            (TRANSLATIONS["invoice_no"], 10, TRANSLATIONS["invoice_info"], "Metin", None),
            (TRANSLATIONS["company"], 11, TRANSLATIONS["invoice_info"], "Metin", None),
            ("Bağışçı", 12, TRANSLATIONS["invoice_info"], "Metin", None),
            ("Özellikler", 13, TRANSLATIONS["invoice_info"], "Metin", None),
            (TRANSLATIONS["status"], 14, TRANSLATIONS["service_info"], "Metin", None),
            (TRANSLATIONS["warranty_period"], 15, TRANSLATIONS["service_info"], "Tarih", None),
            (TRANSLATIONS["description"], 16, TRANSLATIONS["service_info"], "Metin", None)
        ]

        cursor.execute("SELECT column_name FROM metadata")
        existing_columns = [row[0] for row in cursor.fetchall()]
        for column_name, order, section, param_type, combobox_file in default_metadata:
            if column_name not in existing_columns:
                cursor.execute("INSERT INTO metadata (column_name, column_order, section, type, combobox_file) VALUES (?, ?, ?, ?, ?)",
                               (column_name, order, section, param_type, combobox_file))
            elif column_name in [TRANSLATIONS["group_name"], TRANSLATIONS["region"], TRANSLATIONS["floor"]]:
                cursor.execute("UPDATE metadata SET combobox_file = ? WHERE column_name = ?", (combobox_file, column_name))
        self.conn.commit()

    def get_column_headers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name FROM metadata ORDER BY column_order")
        headers = [row[0] for row in cursor.fetchall()]
        logging.info(f"Current column headers: {headers}")
        return headers

class ColumnSelectionDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sütun Seçimi")
        self.headers = headers
        self.selected_headers = []

        layout = QVBoxLayout(self)
        self.checkboxes = {}
        for header in headers:
            checkbox = QCheckBox(header)
            checkbox.setChecked(True)
            self.checkboxes[header] = checkbox
            layout.addWidget(checkbox)

        button_layout = QHBoxLayout()
        select_all_button = QPushButton("Hepsini Seç")
        select_all_button.clicked.connect(self.select_all)
        button_layout.addWidget(select_all_button)

        deselect_all_button = QPushButton("Hepsini Kaldır")
        deselect_all_button.clicked.connect(self.deselect_all)
        button_layout.addWidget(deselect_all_button)

        layout.addLayout(button_layout)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def select_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(True)

    def deselect_all(self):
        for checkbox in self.checkboxes.values():
            checkbox.setChecked(False)

    def get_selected_columns(self):
        self.selected_headers = [header for header, checkbox in self.checkboxes.items() if checkbox.isChecked()]
        return self.selected_headers

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())