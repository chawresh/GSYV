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
from PyQt5.QtGui import QFont, QPixmap
import os
import shutil
import logging
import glob
import time
from datetime import datetime
from datetime import datetime
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

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
    "about_description": "Bu uygulama, GALATASARAYLILAR YURDU envanterini etkili bir şekilde yönetmek ve takip etmek için geliştirilmiştir. Kullanıcı dostu arayüzü ile envanter kayıtlarını ekleme, düzenleme, arşivleme ve analiz etme imkanı sunar.",
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
    "note": "Not"
}

DEFAULT_GROUPS = ["Genel", "Mobilya", "Mutfak", "Elektronik", "Bakım Malzemesi", "Temizlik"]
DEFAULT_USERS = ["Müdür", "Güvenlik", "Sosyal Hizmet"]
DEFAULT_REGIONS = ["Salon", "Mutfak", "Müdür Odası", "Teras"]
DEFAULT_FLOORS = ["Kat -2", "Kat -1", "Kat 0", "Kat 1", "Kat 2", "Kat 3", "Kat 4", "Kat 5"]

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
            self.list_widget.addItem(QListWidgetItem(item))
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
        if ok and new_item.strip() and new_item.strip() not in self.items:
            self.items.append(new_item.strip())
            self.list_widget.addItem(QListWidgetItem(new_item.strip()))
            self.save_items()

    def edit_item(self):
        selected = self.list_widget.currentItem()
        if selected:
            old_item = selected.text()
            new_item, ok = QInputDialog.getText(self, "Öğe Düzenle", "Yeni adı girin:", text=old_item)
            if ok and new_item.strip() and new_item.strip() != old_item:
                self.items[self.items.index(old_item)] = new_item.strip()
                selected.setText(new_item.strip())
                self.save_items()

    def delete_item(self):
        selected = self.list_widget.currentItem()
        if selected:
            item = selected.text()
            if QMessageBox.question(self, "Silme Onayı", f"'{item}' öğesini silmek istediğinizden emin misiniz?",
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                self.items.remove(item)
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
            if header == TRANSLATIONS["group_name"]:
                combo = QComboBox()
                combo.addItems(self.parent.groups)
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header == TRANSLATIONS["region"]:
                combo = QComboBox()
                combo.addItems(self.parent.regions)
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header == TRANSLATIONS["floor"]:
                combo = QComboBox()
                combo.addItems(self.parent.floors)
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header == TRANSLATIONS["user"]:
                combo = QComboBox()
                combo.addItems(self.parent.users)
                combo.setCurrentText(self.row_data[i])
                combo.setEditable(True)
                self.entries[header] = combo
            elif header in [TRANSLATIONS["purchase_date"], TRANSLATIONS["warranty_period"]]:
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                try:
                    date_edit.setDate(datetime.strptime(self.row_data[i], "%d.%m.%Y"))
                except ValueError:
                    date_edit.setDate(datetime.now().date())
                self.entries[header] = date_edit
            else:
                entry = QLineEdit(self.row_data[i])
                self.entries[header] = entry
            layout.addRow(label, self.entries[header])

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        data = []
        for header in self.headers:
            if header in self.entries:
                if isinstance(self.entries[header], QComboBox):
                    value = self.entries[header].currentText()
                elif isinstance(self.entries[header], QDateEdit):
                    value = self.entries[header].date().toString("dd.MM.yyyy")
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

        # Font kontrolü ve yükleme
        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                self.default_font = "DejaVuSans"
                logging.info(f"DejaVuSans.ttf başarıyla yüklendi: {font_path}")
            else:
                pdfmetrics.registerFont(TTFont("Helvetica", "Helvetica"))
                logging.warning(f"DejaVuSans.ttf bulunamadı: {font_path}, Helvetica kullanılıyor.")
        except Exception as e:
            logging.error(f"Font kaydı hatası: {str(e)}. Helvetica kullanılıyor.")
            self.default_font = "Helvetica"
            pdfmetrics.registerFont(TTFont("Helvetica", "Helvetica"))

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

    def add_new_combo_item(self, combo_box, data_list, file_path):
        new_item = combo_box.currentText().strip()
        if new_item and new_item not in data_list:
            data_list.append(new_item)
            combo_box.addItem(new_item)
            self.save_json_data(file_path, data_list)
            self.update_comboboxes()
            logging.info(f"Yeni öğe '{new_item}' {file_path} dosyasına eklendi.")

    def update_comboboxes(self):
        if hasattr(self, 'group_combo'):
            self.group_combo.clear()
            self.group_combo.addItems(self.groups)
        if TRANSLATIONS["user"] in self.card_entries:
            self.card_entries[TRANSLATIONS["user"]].clear()
            self.card_entries[TRANSLATIONS["user"]].addItems(self.users)
        if TRANSLATIONS["region"] in self.card_entries:
            self.card_entries[TRANSLATIONS["region"]].clear()
            self.card_entries[TRANSLATIONS["region"]].addItems(self.regions)
        if TRANSLATIONS["floor"] in self.card_entries:
            self.card_entries[TRANSLATIONS["floor"]].clear()
            self.card_entries[TRANSLATIONS["floor"]].addItems(self.floors)
        if hasattr(self, 'default_group_combo'):
            self.default_group_combo.clear()
            self.default_group_combo.addItems(self.groups)
        if hasattr(self, 'startup_group_combo'):
            self.startup_group_combo.clear()
            self.startup_group_combo.addItems(self.groups + ["Son Kullanılan"])
        if hasattr(self, 'filter_combo'):
            self.filter_combo.clear()
            self.filter_combo.addItem("Tümü")
            self.filter_combo.addItems(self.groups)

    def get_widget_value(self, widget):
        """Widget türlerine göre uygun değeri döndürür."""
        if isinstance(widget, QComboBox):
            return widget.currentText()
        elif isinstance(widget, QDateEdit):
            return widget.date().toString("dd.MM.yyyy")
        elif isinstance(widget, QTextEdit):
            return widget.toPlainText()
        elif hasattr(widget, 'text'):
            return widget.text()
        return ""

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
            if header == TRANSLATIONS["group_name"]:
                self.group_combo = QComboBox()
                self.group_combo.addItems(self.groups)
                self.group_combo.setEditable(True)
                self.group_combo.lineEdit().returnPressed.connect(lambda: self.add_new_combo_item(self.group_combo, self.groups, GROUPS_FILE))
                self.card_entries[header] = self.group_combo
                if self.config["startup_group"] != "Son Kullanılan" and self.config["startup_group"] in self.groups:
                    self.group_combo.setCurrentText(self.config["startup_group"])
            elif header in [TRANSLATIONS["purchase_date"], TRANSLATIONS["warranty_period"]]:
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                date_edit.setDate(datetime.now().date())
                self.card_entries[header] = date_edit
            elif header == TRANSLATIONS["user"]:
                user_combo = QComboBox()
                user_combo.addItems(self.users)
                user_combo.setEditable(True)
                user_combo.lineEdit().returnPressed.connect(lambda: self.add_new_combo_item(user_combo, self.users, USERS_FILE))
                self.card_entries[header] = user_combo
            elif header == TRANSLATIONS["region"]:
                region_combo = QComboBox()
                region_combo.addItems(self.regions)
                region_combo.setEditable(True)
                region_combo.lineEdit().returnPressed.connect(lambda: self.add_new_combo_item(region_combo, self.regions, REGIONS_FILE))
                self.card_entries[header] = region_combo
            elif header == TRANSLATIONS["floor"]:
                floor_combo = QComboBox()
                floor_combo.addItems(self.floors)
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
                date_edit = QDateEdit()
                date_edit.setCalendarPopup(True)
                date_edit.setDisplayFormat("dd.MM.yyyy")
                date_edit.setDate(datetime.now().date())
                self.service_entries[key] = date_edit
            elif key == TRANSLATIONS["note"]:
                entry = QTextEdit()
                entry.setMaximumHeight(60)
                entry.setAcceptRichText(False)
                self.service_entries[key] = entry
            else:
                entry = QLineEdit()
                self.service_entries[key] = entry
            self.service_layout.addRow(label, self.service_entries[key])
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
        self.filter_combo.addItems(self.groups)
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
        self.startup_group_combo.addItems(self.groups + ["Son Kullanılan"])
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
        self.default_group_combo.addItems(self.groups)
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
        """Hakkında sekmesini dinamik ve güzel bir tasarımla ayarlar."""
        # Mevcut düzeni temizle veya yeni düzen oluştur
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

        # Stil sabitleri
        CONTAINER_STYLE = "background: #f1faee; border-radius: 15px; padding: 20px; border: 1px solid #dfe6e9;"
        TITLE_STYLE = "color: #e63946; font-size: 20px; font-weight: bold; font-family: Arial, sans-serif;"
        TEXT_STYLE = "color: #457b9d; font-size: 14px; font-family: Arial, sans-serif;"
        SUBTEXT_STYLE = "color: #6c757d; font-size: 12px;"
        LINK_STYLE = "color: #1d3557; text-decoration: none;"
        LINK_HOVER = "color: #457b9d;"

        # Dinamik veri kaynağı (örnek bir sözlük, veritabanından da alınabilir)
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
                "social": {"GitHub": "https://github.com/chawresh"}
            },
            "copyright": TRANSLATIONS.get("about_copyright", "© 2025 Mustafa AKBAL. Tüm hakları saklıdır.")
        }

        # Ana kapsayıcı
        container = QWidget()
        container.setStyleSheet(CONTAINER_STYLE)
        container.setFixedWidth(500)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(15)

        # Dinamik HTML içeriği oluşturma
        def generate_html(data):
            # Logo kontrolü
            logo_html = f'<img src="{LOGO_FILE}" width="100" height="100" style="border-radius: 50%; border: 2px solid #e63946;">'
            if not os.path.exists(LOGO_FILE):
                logo_html = '<p style="{TEXT_STYLE} text-align: center;">Logo bulunamadı</p>'

            # Sosyal medya bağlantıları
            social_links = "".join(
                f'<a href="{url}" style="{LINK_STYLE}" onmouseover="this.style.color=\'{LINK_HOVER}\';" onmouseout="this.style.color=\'#1d3557\';">{name}</a>' + (" " if i < len(data["developer"]["social"]) - 1 else "")
                for i, (name, url) in enumerate(data["developer"]["social"].items())
            )

            about_html = f"""
            <html>
            <body style="{TEXT_STYLE}">
                <!-- Logo -->
                <div style="text-align: center; margin-bottom: 20px;">
                    {logo_html}
                </div>

                <!-- Başlık -->
                <h1 style="{TITLE_STYLE} text-align: center; margin: 0;">
                    {data["title"]}
                </h1>

                <!-- Versiyon bilgisi -->
                <p style="{SUBTEXT_STYLE} text-align: center; margin: 10px 0;">
                    Sürüm: {data["version"]} • Güncelleme: {data["update_date"]}
                </p>

                <!-- Açıklama -->
                <p style="{TEXT_STYLE} text-align: center; margin: 15px 0; line-height: 1.5;">
                    {data["description"]}
                </p>

                <!-- İletişim bilgileri -->
                <p style="{TEXT_STYLE} text-align: center; margin: 15px 0; line-height: 1.5;">
                    <b>Adres:</b> {data["contact"]["address"]}<br>
                    <b>E-posta:</b> <a href="mailto:{data["contact"]["email"]}" style="{LINK_STYLE}" onmouseover="this.style.color='{LINK_HOVER}';" onmouseout="this.style.color='#1d3557';">{data["contact"]["email"]}</a><br>
                    <b>Telefon:</b> {data["contact"]["phone"]}
                </p>

                <!-- Geliştirici bilgileri -->
                <p style="{TEXT_STYLE} text-align: center; margin: 15px 0; line-height: 1.5;">
                    <b>Geliştirici:</b> {data["developer"]["name"]}<br>
                    <b>E-posta:</b> <a href="mailto:{data["developer"]["email"]}" style="{LINK_STYLE}" onmouseover="this.style.color='{LINK_HOVER}';" onmouseout="this.style.color='#1d3557';">{data["developer"]["email"]}</a><br>
                    <b>Sosyal:</b> {social_links}
                </p>

                <!-- Telif hakkı -->
                <p style="{SUBTEXT_STYLE} text-align: center; font-style: italic; margin-top: 20px;">
                    {data["copyright"]}
                </p>
            </body>
            </html>
            """
            return about_html

        # HTML içeriğini QLabel ile göster
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
            self.archive_table.item(row_idx, 0).setData(Qt.UserRole, row_id)

    def add_item(self):
        headers = self.get_column_headers()
        data = []
        for header in headers:
            if header in self.card_entries:
                value = self.get_widget_value(self.card_entries[header])
            elif header in self.invoice_entries:
                value = self.get_widget_value(self.invoice_entries[header])
            elif header in self.service_entries:
                value = self.get_widget_value(self.service_entries[header])
            else:
                value = ""
            data.append(value)

        group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
        item_name_idx = headers.index(TRANSLATIONS["item_name"]) if TRANSLATIONS["item_name"] in headers else -1

        if group_name_idx == -1 or item_name_idx == -1 or not data[group_name_idx] or not data[item_name_idx]:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_all_fields"])
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(data), timestamp))
        self.conn.commit()
        self.load_data_from_db()
        QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_added"])
        for entry in list(self.card_entries.values()) + list(self.invoice_entries.values()) + list(self.service_entries.values()):
            if isinstance(entry, QLineEdit):
                entry.clear()
            elif isinstance(entry, QDateEdit):
                entry.setDate(datetime.now().date())
            elif isinstance(entry, QTextEdit):
                entry.clear()

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
        if selected >= 0:
            headers = self.get_column_headers()
            data = [self.table.item(selected, col).text() if self.table.item(selected, col) else "" for col in range(len(headers))]
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
        format = self.config["export_format"]
        file_path, _ = QFileDialog.getSaveFileName(self, "Dosyayı Kaydet", "", format)
        if file_path:
            try:
                headers = self.get_column_headers() + [TRANSLATIONS["last_updated"]]
                data = [[self.table.item(row, col).text() if self.table.item(row, col) else "" for col in range(self.table.columnCount())] for row in range(self.table.rowCount())]
                if format == "Excel (*.xlsx)":
                    pd.DataFrame(data, columns=headers).to_excel(file_path, index=False)
                elif format == "CSV (*.csv)":
                    pd.DataFrame(data, columns=headers).to_csv(file_path, index=False)
                elif format == "JSON (*.json)":
                    with open(file_path, 'w', encoding='utf-8') as f:
                        json.dump({h: [row[i] for row in data] for i, h in enumerate(headers)}, f, ensure_ascii=False, indent=4)
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["excel_exported"])
            except Exception as e:
                logging.error(f"Dosyaya aktarma hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", "Dosyaya aktarma sırasında bir hata oluştu.")

    def import_from_file(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "", "Excel (*.xlsx);;CSV (*.csv);;JSON (*.json)")
        if file_path:
            try:
                cursor = self.conn.cursor()
                headers = self.get_column_headers()
                
                # Dosya türüne göre veriyi oku
                if file_path.endswith('.xlsx'):
                    df = pd.read_excel(file_path)
                elif file_path.endswith('.csv'):
                    df = pd.read_csv(file_path)
                elif file_path.endswith('.json'):
                    with open(file_path, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                    df = pd.DataFrame(data)

                # Kullanıcıya ekleme veya üzerine yazma seçeneği sor
                msg = QMessageBox(self)
                msg.setWindowTitle("Veritabanı İçe Aktarma")
                msg.setText("Veriler mevcut veritabanına eklensin mi, yoksa mevcut verilerin üzerine yazılsın mı?")
                msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
                msg.button(QMessageBox.Yes).setText("Ekle")
                msg.button(QMessageBox.No).setText("Üzerine Yaz")
                msg.button(QMessageBox.Cancel).setText("İptal")
                
                response = msg.exec_()
                
                if response == QMessageBox.Cancel:
                    return  # İşlemi iptal et
                
                # Eğer üzerine yaz seçildiyse, mevcut verileri sil
                if response == QMessageBox.No:  # Üzerine Yaz
                    cursor.execute("DELETE FROM inventory")  # Mevcut verileri temizle
                    self.conn.commit()
                    logging.info("Mevcut envanter verileri temizlendi (Üzerine Yaz seçeneği).")

                # Yeni verileri ekle
                for _, row in df.iterrows():
                    data = [str(row.get(header, "")) for header in headers]
                    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(data), timestamp))
                
                self.conn.commit()
                self.load_data_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["excel_imported"])
                logging.info(f"Veriler başarıyla içe aktarıldı: {file_path}")
                
            except Exception as e:
                logging.error(f"Dosyadan içe aktarma hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", "Dosyadan içe aktarma sırasında bir hata oluştu.")

    def generate_pdf_report(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "PDF Kaydet", "", "PDF Files (*.pdf)")
        if file_path:
            try:
                doc = SimpleDocTemplate(file_path, pagesize=landscape(A4), leftMargin=1*cm, rightMargin=1*cm, topMargin=1*cm, bottomMargin=1*cm)
                elements = []
                styles = getSampleStyleSheet()

                title_style = styles['Title']
                title_style.fontName = self.default_font
                title_style.fontSize = 12
                title_style.alignment = 1
                title_style.textColor = colors.HexColor('#D32F2F')

                normal_style = styles['Normal']
                normal_style.fontName = self.default_font
                normal_style.fontSize = 9
                normal_style.alignment = 1
                normal_style.textColor = colors.black

                elements.append(Paragraph("GALATASARAYLILAR YURDU Envanter Raporu", title_style))
                elements.append(Spacer(1, 10))

                if os.path.exists(LOGO_FILE):
                    logo = Image(LOGO_FILE, width=2*cm, height=2*cm)
                    elements.append(logo)
                    elements.append(Spacer(1, 10))

                institution_info = """
                <b>GALATASARAYLILAR YURDU</b><br/>
                Adres: Florya, Şenlikköy Mh. Orman Sk. No:39/1 Florya Bakırköy/İstanbul<br/>
                E-posta: bilgi@gsyardimlasmavakfi.org<br/>
                E-posta: yonetim@gsyardimlasmavakfi.org<br/>
                Telefon: (0212) 574 52 55<br/>
                Telefon: (0532) 448 21 55<br/>
                Rapor Tarihi: {}
                """.format(datetime.now().strftime('%d.%m.%Y %H:%M:%S'))
                institution_para = Paragraph(institution_info, normal_style)
                elements.append(institution_para)
                elements.append(Spacer(1, 20))

                all_headers = self.get_column_headers() + [TRANSLATIONS["last_updated"]]
                dialog = ColumnSelectionDialog(all_headers, self)
                if dialog.exec_():
                    selected_headers = dialog.get_selected_columns()
                    data = [selected_headers]
                    header_indices = [all_headers.index(header) for header in selected_headers]

                    max_length = 20
                    for row in range(self.table.rowCount()):
                        row_data = []
                        for col in header_indices:
                            text = self.table.item(row, col).text() if self.table.item(row, col) else ""
                            if len(text) > max_length:
                                text = text[:max_length - 3] + "..."
                            row_data.append(text)
                        data.append(row_data)

                    col_widths = [min(max(len(str(data[row][col])) for row in range(len(data))) * 5, 100) for col in range(len(selected_headers))]
                    available_width = landscape(A4)[0] - 2 * cm
                    if sum(col_widths) > available_width:
                        scale_factor = available_width / sum(col_widths)
                        col_widths = [w * scale_factor for w in col_widths]

                    table = Table(data, colWidths=col_widths)
                    table.setStyle(TableStyle([
                        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
                        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                        ('FONTNAME', (0, 0), (-1, -1), self.default_font),
                        ('FONTSIZE', (0, 0), (-1, -1), 8),
                        ('LEADING', (0, 0), (-1, -1), 10),
                        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#D32F2F')),
                        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey]),
                        ('BOX', (0, 0), (-1, -1), 1, colors.black),
                        ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),
                    ]))
                    elements.append(table)

                    doc.build(elements)
                    QMessageBox.information(self, "Başarılı", TRANSLATIONS["pdf_generated"])
            except Exception as e:
                logging.error(f"PDF oluşturma hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", "PDF raporu oluşturulurken bir hata oluştu.")

    def edit_combobox(self, title, items, file_path):
        dialog = ComboBoxEditDialog(self, title, items, file_path)
        dialog.exec_()

    def manual_backup(self):
        try:
            backup_dir = self.config["backup_path"]
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"inventory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy(DB_FILE, backup_file)
            self.update_backup_retention()
            QMessageBox.information(self, "Başarılı", TRANSLATIONS["db_backed_up"])
        except Exception as e:
            logging.error(f"Manuel yedekleme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", "Yedekleme sırasında bir hata oluştu.")

    def auto_backup(self):
        try:
            backup_dir = self.config["backup_path"]
            os.makedirs(backup_dir, exist_ok=True)
            backup_file = os.path.join(backup_dir, f"inventory_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.db")
            shutil.copy(DB_FILE, backup_file)
            self.update_backup_retention()
        except Exception as e:
            logging.error(f"Otomatik yedekleme hatası: {str(e)}")

    def data_analysis(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["analysis_title"])
        layout = QVBoxLayout(dialog)
        text = QTextEdit()
        text.setReadOnly(True)
        cursor = self.conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM inventory")
        total = cursor.fetchone()[0]
        analysis_text = f"{TRANSLATIONS['total_records'].format(total)}\n\n"
        cursor.execute("SELECT data FROM inventory")
        rows = cursor.fetchall()
        group_counts = {}
        for row in rows:
            data = json.loads(row[0])
            group = data[0]
            group_counts[group] = group_counts.get(group, 0) + 1
        analysis_text += TRANSLATIONS["group_distribution"] + "\n"
        for group, count in group_counts.items():
            analysis_text += f"{group}: {count}\n"
        text.setText(analysis_text)
        layout.addWidget(text)
        close_button = QPushButton(TRANSLATIONS["close_item"])
        close_button.clicked.connect(dialog.accept)
        layout.addWidget(close_button)
        dialog.exec_()

    def quick_search(self, text):
        for row in range(self.table.rowCount()):
            row_hidden = True
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    row_hidden = False
                    break
            self.table.setRowHidden(row, row_hidden)

    def filter_data(self, group):
        cursor = self.conn.cursor()
        headers = self.get_column_headers()
        if group == "Tümü":
            cursor.execute("SELECT id, data, timestamp FROM inventory")
        else:
            cursor.execute("SELECT id, data, timestamp FROM inventory WHERE json_extract(data, '$[0]') = ?", (group,))
        rows = cursor.fetchall()
        self.table.setRowCount(len(rows))
        for row_idx, (row_id, row_data, timestamp) in enumerate(rows):
            data = json.loads(row_data)
            if len(data) < len(headers):
                data.extend([""] * (len(headers) - len(data)))
            for col, value in enumerate(data):
                self.table.setItem(row_idx, col, QTableWidgetItem(str(value)))
            self.table.setItem(row_idx, len(headers), QTableWidgetItem(timestamp))
            self.table.item(row_idx, 0).setData(Qt.UserRole, row_id)

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

        combobox_menu = menu.addMenu(qta.icon('fa5s.list', color='#D32F2F'), TRANSLATIONS["combobox_management"])
        combobox_menu.addAction(qta.icon('fa5s.users', color='#FFC107'), TRANSLATIONS["edit_groups"],
                                lambda: self.edit_combobox(TRANSLATIONS["edit_groups"], self.groups, GROUPS_FILE))
        combobox_menu.addAction(qta.icon('fa5s.user', color='#FFC107'), TRANSLATIONS["edit_users"],
                                lambda: self.edit_combobox(TRANSLATIONS["edit_users"], self.users, USERS_FILE))
        combobox_menu.addAction(qta.icon('fa5s.map', color='#FFC107'), TRANSLATIONS["edit_regions"],
                                lambda: self.edit_combobox(TRANSLATIONS["edit_regions"], self.regions, REGIONS_FILE))
        combobox_menu.addAction(qta.icon('fa5s.building', color='#FFC107'), TRANSLATIONS["edit_floors"],
                                lambda: self.edit_combobox(TRANSLATIONS["edit_floors"], self.floors, FLOORS_FILE))
        menu.exec_(self.tools_button.mapToGlobal(self.tools_button.rect().bottomLeft()))

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
                (TRANSLATIONS["group_name"], 0, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["item_name"], 1, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["purchase_date"], 2, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["purchase_cost"], 3, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["cost_center"], 4, TRANSLATIONS["card_info"]),
                (TRANSLATIONS["warranty_period"], 5, TRANSLATIONS["card_info"]),
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

    def get_column_headers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name FROM metadata ORDER BY column_order")
        headers = [row[0] for row in cursor.fetchall()]
        if headers:
            return headers
        return [
            TRANSLATIONS["group_name"],
            TRANSLATIONS["item_name"],
            TRANSLATIONS["purchase_date"],
            TRANSLATIONS["purchase_cost"],
            TRANSLATIONS["cost_center"],
            TRANSLATIONS["warranty_period"],
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

    def save_current_form(self):
        headers = self.get_column_headers()
        data = []

        for header in headers:
            if header in self.card_entries:
                value = self.get_widget_value(self.card_entries[header])
            elif header in self.invoice_entries:
                value = self.get_widget_value(self.invoice_entries[header])
            elif header in self.service_entries:
                value = self.get_widget_value(self.service_entries[header])
            else:
                value = ""
            data.append(value)

        group_name_idx = headers.index(TRANSLATIONS["group_name"]) if TRANSLATIONS["group_name"] in headers else -1
        item_name_idx = headers.index(TRANSLATIONS["item_name"]) if TRANSLATIONS["item_name"] in headers else -1

        if group_name_idx == -1 or item_name_idx == -1 or not data[group_name_idx] or not data[item_name_idx]:
            logging.info("Zorunlu alanlar eksik, form kaydedilmedi.")
            return

        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor = self.conn.cursor()
            cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (json.dumps(data), timestamp))
            self.conn.commit()
            logging.info("Form verileri otomatik olarak kaydedildi.")
            self.load_data_from_db()
        except sqlite3.Error as e:
            logging.error(f"Form kaydetme hatası: {str(e)}")

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
                if name not in self.groups and "grup" in name.lower():
                    self.groups.append(name)
                    self.save_json_data(GROUPS_FILE, self.groups)
                elif name not in self.users and "kullanan" in name.lower():
                    self.users.append(name)
                    self.save_json_data(USERS_FILE, self.users)
                elif name not in self.regions and "bölge" in name.lower():
                    self.regions.append(name)
                    self.save_json_data(REGIONS_FILE, self.regions)
                elif name not in self.floors and "kat" in name.lower():
                    self.floors.append(name)
                    self.save_json_data(FLOORS_FILE, self.floors)
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
        if ok:
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
            self.setup_inventory_tab()
            self.setup_archive_tab()
            self.load_data_from_db()
            self.load_archive_from_db()
            QMessageBox.information(self, "Başarılı", "Parametre silindi!")

    def edit_parameter(self):
        headers = self.get_column_headers()
        current_name, ok = QInputDialog.getItem(self, TRANSLATIONS["edit_parameter"],
                                                "Düzenlenecek Parametre:", headers, 0, False)
        if ok:
            dialog = EditParameterDialog(self, current_name)
            if dialog.exec_():
                new_name, section = dialog.get_data()
                if not new_name:
                    QMessageBox.warning(self, "Hata", "Parametre adı boş olamaz!")
                    return
                if new_name in headers and new_name != current_name:
                    QMessageBox.warning(self, "Hata", "Bu isimde bir parametre zaten var!")
                    return
                cursor = self.conn.cursor()
                cursor.execute("UPDATE metadata SET column_name = ?, section = ? WHERE column_name = ?",
                               (new_name, section, current_name))
                self.conn.commit()
                self.setup_inventory_tab()
                self.setup_archive_tab()
                self.load_data_from_db()
                self.load_archive_from_db()
                QMessageBox.information(self, "Başarılı", "Parametre güncellendi!")

    def close_application(self):
        self.save_config()
        self.conn.close()
        self.backup_timer.stop()
        self.autosave_timer.stop()
        QApplication.quit()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())