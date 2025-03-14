import sys
import sqlite3
import json
import pandas as pd
import qtawesome as qta
import platform
import uuid
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QTableWidget, QTableWidgetItem, QPushButton, QLineEdit, QGroupBox,
                             QFileDialog, QInputDialog, QLabel, QMessageBox, QDialog,
                             QFormLayout, QDialogButtonBox, QComboBox, QTextEdit,
                             QTabWidget, QMenu, QSpinBox, QCheckBox, QAbstractItemView, QDateEdit,
                             QListWidget, QListWidgetItem, QProgressDialog)
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
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import mplcursors

# Uygulamanın çalıştığı dizini dinamik olarak belirlemek için yardımcı fonksiyonlar
def get_base_path():
    """ Uygulamanın çalıştığı dizini döndürür """
    if getattr(sys, 'frozen', False):
        return os.path.dirname(sys.argv[0])
    else:
        return os.path.dirname(os.path.abspath(__file__))

def resource_path(relative_path):
    """ PyInstaller ile paketlendiğinde kaynak dosyalarına doğru yolu döndürür """
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    else:
        return os.path.join(os.path.dirname(os.path.abspath(__file__)), relative_path)

# BASE_DIR uygulamanın çalıştığı dizin olarak ayarlanıyor
BASE_DIR = get_base_path()

# Log dosyası doğrudan BASE_DIR içinde
logging.basicConfig(filename=os.path.join(BASE_DIR, 'inventory.log'),
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Sabitler doğrudan BASE_DIR içinde
GROUPS_FILE = os.path.join(BASE_DIR, "groups.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
DB_FILE = os.path.join(BASE_DIR, "inventory.db")
LOGO_FILE = resource_path(os.path.join("files", "logo.png"))  # Statik dosya, paket içinde
REGIONS_FILE = os.path.join(BASE_DIR, "regions.json")
FLOORS_FILE = os.path.join(BASE_DIR, "floors.json")
PHOTO_DIR = BASE_DIR  # Fotoğraflar doğrudan BASE_DIR içinde
BACKUP_DIR = os.path.join(BASE_DIR, "backups")  # Yedekleme dizini

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
    "manual_backup": "Manuel Yedekleme",
    "data_analysis": "Veri Analizi",
    "param_management": "Parametre Yönetimi",
    "backup_operations": "Yedekleme İşlemleri",
    "restore_backup": "Yedeği Geri Yükle",
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
    "export_analysis_data": "Analiz Verilerini Dışa Aktar",
    "confirm_restore_1": "Seçilen yedeği geri yüklemek istediğinizden emin misiniz? Mevcut veritabanı değiştirilecektir.",
    "confirm_restore_2": "Bu işlem mevcut verilerinizi değiştirebilir. Devam etmek istiyor musunuz?",
    "confirm_restore_3": "Son onay: Geri yükleme işlemi geri alınamaz. Onaylıyor musunuz?",
    "restore_success": "Yedek başarıyla geri yüklendi!"
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

class ColumnSelectionDialog(QDialog):
    def __init__(self, headers, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Sütun Seçimi")
        self.headers = headers
        self.checkboxes = {}

        layout = QVBoxLayout(self)
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
        return [header for header, checkbox in self.checkboxes.items() if checkbox.isChecked()]

class AddParameterDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle(TRANSLATIONS["add_parameter"])
        self.entries = {}
        self.sections = ["Kart Bilgileri", "Fatura Bilgileri", "Servis Bilgileri"]
        self.param_types = ["Metin", "ComboBox", "Tarih"]
        self.parent = parent  # Üst sınıfı erişmek için

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

        # Dosya yolu alanını kaldırıyoruz; ComboBox için otomatik oluşturacağız
        self.file_path = None  # Dosya yolunu saklamak için

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def get_data(self):
        param_name = self.entries["Parameter Name"].text().strip()
        section = self.section_combo.currentText()
        param_type = self.type_combo.currentText()

        # ComboBox seçildiyse dosya yolunu otomatik oluştur
        if param_type == "ComboBox":
            # Parametre adına göre benzersiz bir dosya adı oluştur
            file_name = f"{param_name.lower().replace(' ', '_')}.json"
            self.file_path = os.path.join(BASE_DIR, file_name)
            # Boş bir JSON dosyası oluştur (varsayılan değerlerle)
            if not os.path.exists(self.file_path):
                try:
                    with open(self.file_path, 'w', encoding='utf-8') as f:
                        json.dump([], f, ensure_ascii=False, indent=4)  # Boş liste ile başlat
                    logging.info(f"Yeni ComboBox dosyası oluşturuldu: {self.file_path}")
                except IOError as e:
                    logging.error(f"Dosya oluşturma hatası: {str(e)}")
                    QMessageBox.critical(self, "Hata", f"Dosya oluşturulamadı: {str(e)}")
        else:
            self.file_path = None

        return (param_name, section, param_type, self.file_path)

class ComboBoxEditDialog(QDialog):
    def __init__(self, parent=None, title="", items=None, file_path=""):
        super().__init__(parent=parent)
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
        try:
            with open(self.file_path, 'w', encoding='utf-8') as f:
                json.dump(self.items, f, ensure_ascii=False, indent=4)
            self.parent.update_comboboxes()
        except PermissionError as e:
            logging.error(f"{self.file_path} kaydedilirken izin hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosyaya yazma izni yok: {self.file_path}")
        except IOError as e:
            logging.error(f"{self.file_path} kaydedilirken hata: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosya yazılamadı: {self.file_path}")

class EditDialog(QDialog):
    def __init__(self, parent=None, row_data=None, headers=None):
        super().__init__(parent)
        self.setWindowTitle("Envanter Düzenle")
        self.parent = parent
        self.headers = headers or []
        self.entries = {}

        cursor = self.parent.conn.cursor()
        if row_data:
            if isinstance(row_data[0], QTableWidgetItem):
                row_id = row_data[0].data(Qt.UserRole)
                cursor.execute("SELECT data FROM inventory WHERE id = ?", (row_id,))
                full_data = json.loads(cursor.fetchone()[0])
            elif isinstance(row_data[0], str):
                full_data = row_data
            else:
                raise ValueError("EditDialog: row_data beklenmeyen bir türde.")
        else:
            full_data = [""] * len(self.headers)

        self.row_data = full_data if len(full_data) >= len(self.headers) else full_data + [""] * (len(self.headers) - len(full_data))
        if len(self.row_data) > len(self.headers):
            self.row_data = self.row_data[:len(self.headers)]

        layout = QFormLayout(self)
        cursor.execute("SELECT column_name, type, combobox_file FROM metadata ORDER BY column_order")
        metadata = cursor.fetchall()
        param_types = {row[0]: (row[1], row[2]) for row in metadata}

        for i, header in enumerate(self.headers):
            label = QLabel(header)
            param_type, combobox_file = param_types.get(header, ("Metin", None))
            current_value = self.row_data[i]

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
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            extension = os.path.splitext(file_name)[1]
            new_file_name = os.path.join(PHOTO_DIR, f"photo_{timestamp}_{unique_id}{extension}")
            try:
                shutil.copy2(file_name, new_file_name)
                entry.setText(os.path.basename(new_file_name))
                logging.info(f"Fotoğraf {new_file_name} olarak kopyalandı.")
            except IOError as e:
                logging.error(f"Fotoğraf kopyalanamadı: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Fotoğraf kopyalanamadı: {str(e)}")

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
        return data

class InventoryApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.os_name = platform.system()
        self.default_font = "DejaVuSans"
        font_path = resource_path(os.path.join("files", "DejaVuSans.ttf"))

        try:
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont("DejaVuSans", font_path))
                logging.info(f"DejaVuSans.ttf başarıyla yüklendi: {font_path}")
                plt.rcParams['font.family'] = 'DejaVu Sans'
            else:
                pdfmetrics.registerFont(TTFont("Helvetica", "Helvetica"))
                self.default_font = "Helvetica"
                logging.warning(f"DejaVuSans.ttf bulunamadı: {font_path}, Helvetica kullanılıyor.")
                plt.rcParams['font.family'] = 'Helvetica'
        except Exception as e:
            logging.error(f"Font kaydı hatası: {str(e)}. Helvetica kullanılıyor.")
            self.default_font = "Helvetica"
            plt.rcParams['font.family'] = 'Helvetica'

        self.setWindowTitle(TRANSLATIONS["title"])
        self.setGeometry(100, 100, 1200, 700)

        self.copy_initial_files()

        self.db_exists = os.path.exists(DB_FILE)
        if self.db_exists:
            try:
                self.conn = sqlite3.connect(DB_FILE)
                logging.info("Mevcut veritabanı bulundu ve bağlanıldı.")
            except sqlite3.Error as e:
                logging.error(f"Veritabanına bağlanılamadı: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Veritabanına bağlanılamadı: {str(e)}")
                sys.exit(1)
        else:
            try:
                self.conn = sqlite3.connect(DB_FILE)
                self.db_exists = True
                logging.info("Veritabanı bulunamadı, yeni bir veritabanı oluşturuldu.")
            except sqlite3.Error as e:
                logging.error(f"Veritabanı oluşturulamadı: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Veritabanı oluşturulamadı: {str(e)}")
                sys.exit(1)
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

    def copy_initial_files(self):
        """ Paket içindeki başlangıç dosyalarını BASE_DIR'e kopyalar """
        initial_files = {
            "groups.json": resource_path(os.path.join("files", "groups.json")),
            "regions.json": resource_path(os.path.join("files", "regions.json")),
            "floors.json": resource_path(os.path.join("files", "floors.json")),
            "inventory.db": resource_path(os.path.join("files", "inventory.db")),
            "config.json": resource_path(os.path.join("files", "config.json")),
            "DejaVuSans.ttf": resource_path(os.path.join("files", "DejaVuSans.ttf"))
        }
        for file_name, src_path in initial_files.items():
            dest_path = os.path.join(BASE_DIR, file_name)
            if not os.path.exists(dest_path) and os.path.exists(src_path):
                try:
                    shutil.copy2(src_path, dest_path)
                    logging.info(f"Başlangıç dosyası kopyalandı: {dest_path}")
                except IOError as e:
                    logging.error(f"Başlangıç dosyası kopyalanamadı: {src_path} -> {dest_path}, Hata: {str(e)}")

    def load_json_data(self, file_path, default_data):
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except (json.JSONDecodeError, IOError) as e:
            logging.error(f"{file_path} yüklenirken hata: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosya yüklenemedi: {file_path}")
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(default_data, f, ensure_ascii=False, indent=4)
        except IOError as e:
            logging.error(f"{file_path} kaydedilirken hata: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosya yazılamadı: {file_path}")
        return default_data

    def save_json_data(self, file_path, data):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
        except PermissionError as e:
            logging.error(f"{file_path} kaydedilirken izin hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosyaya yazma izni yok: {file_path}")
        except IOError as e:
            logging.error(f"{file_path} kaydedilirken hata: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Dosya yazılamadı: {file_path}")

    def generate_shortcode(self, name, existing_codes):
        shortcode = name[:3].upper()
        if shortcode in existing_codes:
            i = 1
            while f"{shortcode}{i}" in existing_codes:
                i += 1
            shortcode = f"{shortcode}{i}"
        return shortcode

    def update_comboboxes(self):
        self.groups = self.load_json_data(GROUPS_FILE, DEFAULT_GROUPS)
        self.regions = self.load_json_data(REGIONS_FILE, DEFAULT_REGIONS)
        self.floors = self.load_json_data(FLOORS_FILE, DEFAULT_FLOORS)

        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name, combobox_file FROM metadata WHERE type = 'ComboBox'")
        combobox_params = cursor.fetchall()

        for header, file_path in combobox_params:
            items = self.load_json_data(file_path, [])
            if header in self.card_entries:
                combo = self.card_entries[header]
                current_text = combo.currentText()
                combo.clear()
                combo.addItems([item["name"] for item in items])
                combo.setCurrentText(current_text if current_text in [item["name"] for item in items] else "")
            elif header in self.invoice_entries:
                combo = self.invoice_entries[header]
                current_text = combo.currentText()
                combo.clear()
                combo.addItems([item["name"] for item in items])
                combo.setCurrentText(current_text if current_text in [item["name"] for item in items] else "")
            elif header in self.service_entries:
                combo = self.service_entries[header]
                current_text = combo.currentText()
                combo.clear()
                combo.addItems([item["name"] for item in items])
                combo.setCurrentText(current_text if current_text in [item["name"] for item in items] else "")

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

        # Kart Bilgileri
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
                elif header == "Demirbaş Grubu" or header == TRANSLATIONS["group_name"]:
                    combo = QComboBox()
                    items = self.load_json_data(GROUPS_FILE, DEFAULT_GROUPS)
                    combo.addItems([item["name"] for item in items])
                    combo.setEditable(True)
                    if self.config["startup_group"] != "Son Kullanılan" and self.config["startup_group"] in [item["name"] for item in items]:
                        combo.setCurrentText(self.config["startup_group"])
                    self.card_entries[header] = combo
                elif header == TRANSLATIONS["region"]:
                    combo = QComboBox()
                    items = self.load_json_data(REGIONS_FILE, DEFAULT_REGIONS)
                    combo.addItems([item["name"] for item in items])
                    combo.setEditable(True)
                    self.card_entries[header] = combo
                elif header == TRANSLATIONS["floor"]:
                    combo = QComboBox()
                    items = self.load_json_data(FLOORS_FILE, DEFAULT_FLOORS)
                    combo.addItems([item["name"] for item in items])
                    combo.setEditable(True)
                    self.card_entries[header] = combo
                elif param_type == "ComboBox" and combobox_file:
                    combo = QComboBox()
                    items = self.load_json_data(combobox_file, [])
                    combo.addItems([item["name"] for item in items])
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
                    entry.textChanged.connect(lambda text, h=header: self.validate_field(h, text))
                    self.card_entries[header] = entry
            self.card_layout.addRow(label, self.card_entries[header])
        self.card_group.setLayout(self.card_layout)
        top_layout.addWidget(self.card_group)

        # Fatura Bilgileri
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

        # Servis Bilgileri
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

        # Arama ve Filtreleme
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

        # Tablo
        self.table = QTableWidget()
        visible_headers = [h for h in self.get_column_headers() if h != TRANSLATIONS["photo"]] + ["Son Güncelleme"]
        self.table.setColumnCount(len(visible_headers))
        self.table.setHorizontalHeaderLabels(visible_headers)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setSortingEnabled(True)
        self.table.itemDoubleClicked.connect(self.show_details)
        layout.addWidget(self.table)

        # Düğmeler
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
        tools_menu.addSeparator()
        tools_menu.addAction(qta.icon('fa5s.file-export', color='#D32F2F'), TRANSLATIONS["export_charts"], self.export_charts)
        tools_menu.addAction(qta.icon('fa5s.file-download', color='#D32F2F'), TRANSLATIONS["export_analysis_data"], self.export_analysis_data)
        self.tools_button.setMenu(tools_menu)
        button_layout.addWidget(self.tools_button)

        self.close_button = QPushButton(TRANSLATIONS["close_item"])
        self.close_button.setIcon(qta.icon('fa5s.times', color='#D32F2F'))
        self.close_button.clicked.connect(self.close_application)
        button_layout.addWidget(self.close_button)

        layout.addLayout(button_layout)

    def toggle_photo(self, entry, state):
        entry.setEnabled(state == Qt.Unchecked)
        if state == Qt.Checked:
            entry.clear()

    def toggle_donor(self, entry, state):
        entry.setEnabled(state == Qt.Unchecked)
        if state == Qt.Checked:
            entry.clear()

    def select_photo(self, entry):
        file_name, _ = QFileDialog.getOpenFileName(self, "Fotoğraf Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)")
        if file_name:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            unique_id = uuid.uuid4().hex[:8]
            extension = os.path.splitext(file_name)[1]
            new_file_name = os.path.join(PHOTO_DIR, f"photo_{timestamp}_{unique_id}{extension}")
            try:
                shutil.copy2(file_name, new_file_name)
                entry.setText(os.path.basename(new_file_name))
                logging.info(f"Fotoğraf {new_file_name} olarak kopyalandı.")
            except IOError as e:
                logging.error(f"Fotoğraf kopyalanamadı: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Fotoğraf kopyalanamadı: {str(e)}")

    def validate_field(self, header, text):
        if header == TRANSLATIONS["item_name"] and not text.strip():
            self.add_button.setEnabled(False)
        else:
            self.add_button.setEnabled(True)

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
        self.archive_table.setSortingEnabled(True)
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

        self.restore_combo = QComboBox()
        backups = sorted(glob.glob(os.path.join(self.config["backup_path"], "inventory_backup_*.db")), key=os.path.getctime, reverse=True)
        self.restore_combo.addItems([os.path.basename(b) for b in backups[:10]])
        backup_layout.addRow(QLabel(TRANSLATIONS["restore_backup"]), self.restore_combo)

        self.restore_button = QPushButton(TRANSLATIONS["restore_item"])
        self.restore_button.clicked.connect(self.restore_backup)
        backup_layout.addRow("", self.restore_button)

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
            "backup_path": BACKUP_DIR,
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
        self.save_json_data(CONFIG_FILE, self.config)

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
                "backup_path": BACKUP_DIR,
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
            self.backup_path_edit.setText(BACKUP_DIR)
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
        headers = self.get_column_headers()
        visible_headers = [h for h in headers if h != TRANSLATIONS["photo"]] + ["Son Güncelleme"]
        self.table.setColumnCount(len(visible_headers))
        self.table.setHorizontalHeaderLabels(visible_headers)

        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id, data, timestamp FROM inventory")
            rows = cursor.fetchall()
            self.table.setRowCount(len(rows))

            for row_idx, (row_id, data_json, timestamp) in enumerate(rows):
                data = json.loads(data_json)
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
                    item.setData(Qt.UserRole, row_id)
                    self.table.setItem(row_idx, col_idx, item)

            self.table.resizeColumnsToContents()
            logging.info(f"load_data_from_db: Tablo {len(rows)} satırla güncellendi.")
        except sqlite3.Error as e:
            logging.error(f"Veritabanından veri yüklenemedi: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Veritabanından veri yüklenemedi: {str(e)}")

    def load_archive_from_db(self):
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT id, data, timestamp FROM archive")
            rows = cursor.fetchall()
            headers = self.get_column_headers()
            visible_headers = [h for h in headers if h != TRANSLATIONS["photo"]] + ["Son Güncelleme"]
            self.archive_table.setColumnCount(len(visible_headers))
            self.archive_table.setHorizontalHeaderLabels(visible_headers)
            self.archive_table.setRowCount(len(rows))

            for row_idx, (row_id, row_data, timestamp) in enumerate(rows):
                data = json.loads(row_data)
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
                    item.setData(Qt.UserRole, row_id)
                    self.archive_table.setItem(row_idx, col_idx, item)

            self.archive_table.resizeColumnsToContents()
            logging.info(f"load_archive_from_db: Arşiv tablosu {len(rows)} satırla güncellendi.")
        except sqlite3.Error as e:
            logging.error(f"Arşiv veritabanından veri yüklenemedi: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Arşiv veritabanından veri yüklenemedi: {str(e)}")

    def add_item(self):
        headers = self.get_column_headers()
        data = []
        group_name = None
        region_name = None
        floor_name = None
        inventory_code = None

        for header in headers:
            if header in self.card_entries:
                if header == "Edinim Tarihi" or (header in self.card_entries and isinstance(self.card_entries[header], QDateEdit)):
                    if f"{header}_check" in self.card_entries and self.card_entries[f"{header}_check"].isChecked():
                        value = TRANSLATIONS["unknown"]
                    else:
                        value = self.card_entries[header].date().toString("dd.MM.yyyy")
                elif header == TRANSLATIONS["photo"]:
                    if f"{header}_check" in self.card_entries and self.card_entries[f"{header}_check"].isChecked():
                        value = ""
                    else:
                        value = self.card_entries[header].text()
                elif header == TRANSLATIONS["group_name"]:
                    value = self.card_entries[header].currentText()
                    group_name = value
                elif header == TRANSLATIONS["region"]:
                    value = self.card_entries[header].currentText()
                    region_name = value
                elif header == TRANSLATIONS["floor"]:
                    value = self.card_entries[header].currentText()
                    floor_name = value
                else:
                    value = self.get_widget_value(self.card_entries[header])
            elif header in self.invoice_entries:
                if header == "Bağışçı" and f"{header}_check" in self.invoice_entries and self.invoice_entries[f"{header}_check"].isChecked():
                    value = ""
                elif isinstance(self.invoice_entries[header], QDateEdit):
                    if f"{header}_check" in self.invoice_entries and self.invoice_entries[f"{header}_check"].isChecked():
                        value = TRANSLATIONS["unknown"]
                    else:
                        value = self.invoice_entries[header].date().toString("dd.MM.yyyy")
                else:
                    value = self.get_widget_value(self.invoice_entries[header])
            elif header in self.service_entries:
                if header == TRANSLATIONS["warranty_period"] or (header in self.service_entries and isinstance(self.service_entries[header], QDateEdit)):
                    if f"{header}_check" in self.service_entries and self.service_entries[f"{header}_check"].isChecked():
                        value = TRANSLATIONS["unknown"]
                    else:
                        value = self.service_entries[header].date().toString("dd.MM.yyyy")
                else:
                    value = self.get_widget_value(self.service_entries[header])
            else:
                value = ""
            data.append(value)

        if not data[headers.index(TRANSLATIONS["item_name"])].strip():
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_all_fields"])
            return

        if group_name and region_name and floor_name:
            inventory_code = self.generate_inventory_code(group_name, region_name, floor_name)
            data[headers.index("Demirbaş Kodu")] = inventory_code

        cursor = self.conn.cursor()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)",
                           (json.dumps(data), timestamp))
            self.conn.commit()
            self.load_data_from_db()
            self.clear_form()
            QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_added"])
            logging.info(f"Yeni envanter eklendi: {inventory_code}")
        except sqlite3.Error as e:
            logging.error(f"Veritabanına ekleme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Veritabanına eklenemedi: {str(e)}")

    def clear_form(self):
        for entry in self.card_entries.values():
            if isinstance(entry, QLineEdit) and entry != self.card_entries.get("Demirbaş Kodu"):
                entry.clear()
            elif isinstance(entry, QComboBox):
                entry.setCurrentIndex(0)
            elif isinstance(entry, QDateEdit):
                entry.setDate(datetime.now().date())
            elif isinstance(entry, QCheckBox):
                entry.setChecked(False)
            elif isinstance(entry, QTextEdit):
                entry.clear()
        for entry in self.invoice_entries.values():
            if isinstance(entry, QLineEdit):
                entry.clear()
            elif isinstance(entry, QComboBox):
                entry.setCurrentIndex(0)
            elif isinstance(entry, QDateEdit):
                entry.setDate(datetime.now().date())
            elif isinstance(entry, QCheckBox):
                entry.setChecked(False)
            elif isinstance(entry, QTextEdit):
                entry.clear()
        for entry in self.service_entries.values():
            if isinstance(entry, QLineEdit):
                entry.clear()
            elif isinstance(entry, QComboBox):
                entry.setCurrentIndex(0)
            elif isinstance(entry, QDateEdit):
                entry.setDate(datetime.now().date())
            elif isinstance(entry, QCheckBox):
                entry.setChecked(False)
            elif isinstance(entry, QTextEdit):
                entry.clear()
        if "Demirbaş Kodu" in self.card_entries:
            self.card_entries["Demirbaş Kodu"].setText("Otomatik")

    def open_edit_dialog(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        row = self.table.currentRow()
        row_data = [self.table.item(row, col) for col in range(self.table.columnCount())]
        dialog = EditDialog(self, row_data, self.get_column_headers())
        if dialog.exec_() == QDialog.Accepted:
            new_data = dialog.get_data()
            row_id = row_data[0].data(Qt.UserRole)
            cursor = self.conn.cursor()
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                cursor.execute("UPDATE inventory SET data = ?, timestamp = ? WHERE id = ?",
                               (json.dumps(new_data), timestamp, row_id))
                self.conn.commit()
                self.load_data_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_updated"])
                logging.info(f"Envanter güncellendi: ID {row_id}")
            except sqlite3.Error as e:
                logging.error(f"Veritabanı güncelleme hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Veritabanı güncellenemedi: {str(e)}")

    def archive_item_with_confirmation(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        if QMessageBox.question(self, "Onay", TRANSLATIONS["confirm_archive"],
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            row = self.table.currentRow()
            row_id = self.table.item(row, 0).data(Qt.UserRole)
            cursor = self.conn.cursor()
            try:
                cursor.execute("SELECT data, timestamp FROM inventory WHERE id = ?", (row_id,))
                data, timestamp = cursor.fetchone()
                cursor.execute("INSERT INTO archive (data, timestamp) VALUES (?, ?)", (data, timestamp))
                cursor.execute("DELETE FROM inventory WHERE id = ?", (row_id,))
                self.conn.commit()
                self.load_data_from_db()
                self.load_archive_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_archived"])
                logging.info(f"Envanter arşive taşındı: ID {row_id}")
            except sqlite3.Error as e:
                logging.error(f"Arşivleme hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Arşivleme başarısız: {str(e)}")

    def delete_item_with_double_confirmation(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        if QMessageBox.question(self, "Onay", TRANSLATIONS["confirm_delete"],
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            if QMessageBox.question(self, "Son Onay", TRANSLATIONS["confirm_delete_final"],
                                    QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
                row = self.table.currentRow()
                row_id = self.table.item(row, 0).data(Qt.UserRole)
                cursor = self.conn.cursor()
                try:
                    cursor.execute("DELETE FROM inventory WHERE id = ?", (row_id,))
                    self.conn.commit()
                    self.load_data_from_db()
                    QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_deleted"])
                    logging.info(f"Envanter silindi: ID {row_id}")
                except sqlite3.Error as e:
                    logging.error(f"Silme hatası: {str(e)}")
                    QMessageBox.critical(self, "Hata", f"Silme başarısız: {str(e)}")

    def duplicate_item(self):
        selected = self.table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        row = self.table.currentRow()
        row_id = self.table.item(row, 0).data(Qt.UserRole)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT data FROM inventory WHERE id = ?", (row_id,))
            data = json.loads(cursor.fetchone()[0])
            data[headers.index("Demirbaş Kodu")] = self.generate_inventory_code(
                data[headers.index(TRANSLATIONS["group_name"])],
                data[headers.index(TRANSLATIONS["region"])],
                data[headers.index(TRANSLATIONS["floor"])]
            )
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)",
                           (json.dumps(data), timestamp))
            self.conn.commit()
            self.load_data_from_db()
            QMessageBox.information(self, "Başarılı", "Envanter çoğaltıldı!")
            logging.info(f"Envanter çoğaltıldı: Yeni ID {cursor.lastrowid}")
        except sqlite3.Error as e:
            logging.error(f"Çoğaltma hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Çoğaltma başarısız: {str(e)}")

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

            # Fotoğrafı en üste ekle
            photo_idx = headers.index(TRANSLATIONS["photo"]) if TRANSLATIONS["photo"] in headers else -1
            if photo_idx != -1 and data[photo_idx]:
                photo_path = os.path.abspath(os.path.join(BASE_DIR, data[photo_idx]))
                photo_label = QLabel("Demirbaş Fotoğrafı:")
                photo_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                photo_widget = QLabel()

                if os.path.exists(photo_path):
                    pixmap = QPixmap(photo_path)
                    if not pixmap.isNull():
                        pixmap = pixmap.scaled(200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                        photo_widget.setPixmap(pixmap)
                    else:
                        photo_widget.setText(f"Fotoğraf yüklenemedi: {photo_path}")
                        logging.warning(f"Fotoğraf yüklenemedi (QPixmap hatası): {photo_path}")
                else:
                    photo_widget.setText(f"Dosya bulunamadı: {photo_path}")
                    logging.warning(f"Fotoğraf dosyası bulunamadı: {photo_path}")

                layout.addWidget(photo_label)
                layout.addWidget(photo_widget)
                layout.addSpacing(10)
            else:
                photo_label = QLabel("Demirbaş Fotoğrafı: Yok")
                photo_label.setStyleSheet("font-weight: bold; font-size: 14px;")
                layout.addWidget(photo_label)
                layout.addSpacing(10)

            # Sekmeli yapı
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
                if header == TRANSLATIONS["photo"]:  # Fotoğrafı zaten gösterdik, atla
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

            # Demirbaş kodu çözümleme
            code_idx = headers.index("Demirbaş Kodu") if "Demirbaş Kodu" in headers else -1
            if code_idx != -1 and code_idx < len(data):
                code = data[code_idx]
                decoded_info = self.decode_inventory_code(code)
                code_label = QLabel(f"Kod Çözümleme: {decoded_info}")
                code_label.setStyleSheet("font-weight: bold; color: #D32F2F; font-size: 14px; margin-top: 10px;")
                layout.addWidget(code_label)

            # Düğmeler
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

                # Fotoğraf (en üstte)
                photo_idx = headers.index(TRANSLATIONS["photo"]) if TRANSLATIONS["photo"] in headers else -1
                if photo_idx != -1 and data[photo_idx]:
                    photo_path = os.path.abspath(os.path.join(BASE_DIR, data[photo_idx]))
                    if os.path.exists(photo_path):
                        photo = Image(photo_path, width=5 * cm, height=5 * cm)  # Fotoğraf boyutu ayarlanabilir
                        photo.hAlign = 'CENTER'
                        elements.append(photo)
                        elements.append(Spacer(1, 0.5 * cm))
                    else:
                        elements.append(Spacer(1, 0.5 * cm))

                # Başlık (Kurum adı şekillendirildi)
                title_style = ParagraphStyle(
                    'TitleStyle',
                    parent=styles['Heading1'],
                    fontName=self.default_font,
                    fontSize=16,
                    textColor=colors.darkred,  # Koyu kırmızı renk
                    alignment=1,  # Ortala
                    spaceAfter=10,
                    borderWidth=1,  # Çerçeve
                    borderColor=colors.black,
                    borderPadding=5
                )
                title = Paragraph(TRANSLATIONS["details_title"], title_style)
                elements.append(title)
                elements.append(Spacer(1, 0.5 * cm))

                # Kurum adres bilgileri
                address_style = ParagraphStyle(
                    'AddressStyle',
                    parent=styles['Normal'],
                    fontName=self.default_font,
                    fontSize=10,
                    textColor=colors.black,
                    alignment=1,  # Ortala
                    spaceAfter=5
                )
                address_text = (
                    "Florya, Şenlikköy Mh. Orman Sk. No:39/1 Florya Bakırköy/İstanbul<br/>"
                    "E-posta: bilgi@gsyardimlasmavakfi.org | Telefon: (0212) 574 52 55"
                )
                address = Paragraph(address_text, address_style)
                elements.append(address)

                # Oluşturma tarihi
                date_style = ParagraphStyle(
                    'DateStyle',
                    parent=styles['Normal'],
                    fontName=self.default_font,
                    fontSize=9,
                    textColor=colors.grey,
                    alignment=1,  # Ortala
                    spaceAfter=10
                )
                creation_date = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
                date_text = f"Oluşturulma Tarihi: {creation_date}"
                date = Paragraph(date_text, date_style)
                elements.append(date)

                # Logo (varsa)
                if os.path.exists(LOGO_FILE):
                    logo = Image(LOGO_FILE, width=2 * cm, height=2 * cm)
                    logo.hAlign = 'CENTER'
                    elements.append(logo)
                    elements.append(Spacer(1, 0.5 * cm))

                # Tablo verisi
                table_data = [["Alan", "Değer"]]
                for header, value in zip(headers, data):
                    if header != TRANSLATIONS["photo"]:  # Fotoğrafı tabloya eklemiyoruz
                        table_data.append([header, value or "Bilgi Yok"])

                # Tablo oluşturma ve ölçeklendirme
                page_width = A4[0] - 2 * cm  # Kenar boşlukları düşülmüş genişlik
                col_widths = [page_width * 0.35, page_width * 0.65]  # Başlangıç genişlikleri

                table = Table(table_data, colWidths=col_widths)
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
                    ('WORDWRAP', (0, 0), (-1, -1), True),  # Metin kaydırma
                ]))

                # Tabloyu ölçeklendirme
                table_width, table_height = table.wrap(0, 0)  # Tabloyu ölç
                if table_width > page_width:
                    scale_factor = page_width / table_width
                    table = Table(table_data, colWidths=[w * scale_factor for w in col_widths])
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
                        ('WORDWRAP', (0, 0), (-1, -1), True),
                    ]))
                elements.append(table)

                # PDF'i oluştur
                doc.build(elements)
                QMessageBox.information(self, "Başarılı", "Detaylar PDF olarak kaydedildi!")
                logging.info(f"Detaylar PDF olarak {file_name} dosyasına kaydedildi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"PDF oluşturma başarısız: {str(e)}")
                logging.error(f"PDF oluşturma hatası: {str(e)}")

    def view_archive_item(self):
        selected = self.archive_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        row = self.archive_table.currentRow()
        row_id = self.archive_table.item(row, 0).data(Qt.UserRole)
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM archive WHERE id = ?", (row_id,))
        data = json.loads(cursor.fetchone()[0])
        headers = self.get_column_headers()
        details = "\n".join([f"{header}: {value}" for header, value in zip(headers, data)])
        QMessageBox.information(self, TRANSLATIONS["details_title"], details)

    def restore_archive_item(self):
        selected = self.archive_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        row = self.archive_table.currentRow()
        row_id = self.archive_table.item(row, 0).data(Qt.UserRole)
        cursor = self.conn.cursor()
        try:
            cursor.execute("SELECT data, timestamp FROM archive WHERE id = ?", (row_id,))
            data, timestamp = cursor.fetchone()
            cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)", (data, timestamp))
            cursor.execute("DELETE FROM archive WHERE id = ?", (row_id,))
            self.conn.commit()
            self.load_data_from_db()
            self.load_archive_from_db()
            QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_restored"])
            logging.info(f"Envanter geri yüklendi: ID {row_id}")
        except sqlite3.Error as e:
            logging.error(f"Geri yükleme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Geri yükleme başarısız: {str(e)}")

    def delete_archive_item_with_confirmation(self):
        selected = self.archive_table.selectedItems()
        if not selected:
            QMessageBox.warning(self, "Hata", TRANSLATIONS["error_select_row"])
            return
        if QMessageBox.question(self, "Onay", TRANSLATIONS["confirm_delete"],
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            row = self.archive_table.currentRow()
            row_id = self.archive_table.item(row, 0).data(Qt.UserRole)
            cursor = self.conn.cursor()
            try:
                cursor.execute("DELETE FROM archive WHERE id = ?", (row_id,))
                self.conn.commit()
                self.load_archive_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["item_deleted"])
                logging.info(f"Arşivden envanter silindi: ID {row_id}")
            except sqlite3.Error as e:
                logging.error(f"Arşiv silme hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Silme başarısız: {str(e)}")

    def export_to_file(self):
        headers = self.get_column_headers()
        visible_headers = [h for h in headers if h != TRANSLATIONS["photo"]] + ["Son Güncelleme"]
        data = []
        for row in range(self.table.rowCount()):
            row_data = [self.table.item(row, col).text() if self.table.item(row, col) else "" 
                        for col in range(self.table.columnCount())]
            data.append(row_data)

        dialog = ColumnSelectionDialog(visible_headers)
        if dialog.exec_() == QDialog.Accepted:
            selected_columns = dialog.get_selected_columns()
            col_indices = [visible_headers.index(col) for col in selected_columns]
            filtered_data = [[row[i] for i in col_indices] for row in data]

            file_format = self.config["export_format"]
            file_name, _ = QFileDialog.getSaveFileName(self, "Dosyayı Kaydet", "",
                                                       "Excel (*.xlsx);;CSV (*.csv);;JSON (*.json)")
            if file_name:
                try:
                    if file_format == "Excel (*.xlsx)" or file_name.endswith('.xlsx'):
                        df = pd.DataFrame(filtered_data, columns=selected_columns)
                        df.to_excel(file_name, index=False)
                    elif file_format == "CSV (*.csv)" or file_name.endswith('.csv'):
                        df = pd.DataFrame(filtered_data, columns=selected_columns)
                        df.to_csv(file_name, index=False, encoding='utf-8-sig')
                    elif file_format == "JSON (*.json)" or file_name.endswith('.json'):
                        with open(file_name, 'w', encoding='utf-8') as f:
                            json.dump({col: [row[i] for row in filtered_data] 
                                      for i, col in enumerate(selected_columns)}, f, ensure_ascii=False, indent=4)
                    QMessageBox.information(self, "Başarılı", TRANSLATIONS["excel_exported"])
                    logging.info(f"Veriler dosyaya aktarıldı: {file_name}")
                except Exception as e:
                    logging.error(f"Dışa aktarma hatası: {str(e)}")
                    QMessageBox.critical(self, "Hata", f"Dışa aktarma başarısız: {str(e)}")

    def import_from_file(self):
        file_name, _ = QFileDialog.getOpenFileName(self, "Dosya Seç", "",
                                                   "Excel (*.xlsx);;CSV (*.csv);;JSON (*.json)")
        if file_name:
            try:
                if file_name.endswith('.xlsx'):
                    df = pd.read_excel(file_name)
                elif file_name.endswith('.csv'):
                    df = pd.read_csv(file_name, encoding='utf-8-sig')
                elif file_name.endswith('.json'):
                    with open(file_name, 'r', encoding='utf-8') as f:
                        data = json.load(f)
                        df = pd.DataFrame(data)
                else:
                    raise ValueError("Desteklenmeyen dosya formatı")

                headers = self.get_column_headers()
                cursor = self.conn.cursor()
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                progress = QProgressDialog("Veriler içe aktarılıyor...", "İptal", 0, len(df), self)
                progress.setWindowModality(Qt.WindowModal)

                for index, row in df.iterrows():
                    if progress.wasCanceled():
                        break
                    data = []
                    for header in headers:
                        value = row.get(header, "")
                        data.append(str(value) if pd.notna(value) else "")
                    cursor.execute("INSERT INTO inventory (data, timestamp) VALUES (?, ?)",
                                   (json.dumps(data), timestamp))
                    progress.setValue(index + 1)
                    QApplication.processEvents()

                self.conn.commit()
                self.load_data_from_db()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["excel_imported"])
                logging.info(f"Veriler {file_name} dosyasından içe aktarıldı.")
            except Exception as e:
                logging.error(f"İçe aktarma hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"İçe aktarma başarısız: {str(e)}")


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

                    # Tüm veriyi tablo için hazırla
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
                        if photo_idx != -1 and data[photo_idx]:
                            photo_path = os.path.abspath(os.path.join(BASE_DIR, data[photo_idx]))  # Mutlak yol
                            if os.path.exists(photo_path):
                                try:
                                    photo = Image(photo_path, width=1.5 * cm, height=1.5 * cm)  # Boyut artırıldı
                                    row_data.append(photo)
                                except Exception as e:
                                    row_data.append("Fotoğraf Yüklenemedi")
                                    logging.error(f"PDF'de fotoğraf yüklenemedi: {photo_path}, Hata: {str(e)}")
                            else:
                                row_data.append("Fotoğraf Bulunamadı")
                                logging.warning(f"PDF'de fotoğraf dosyası bulunamadı: {photo_path}")
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

                    col_max_lengths = [len(str(table_data[0][i])) for i in range(num_cols)]
                    for row in table_data[1:]:
                        for i, cell in enumerate(row):
                            if i == 0 and isinstance(cell, Image):
                                col_max_lengths[i] = max(col_max_lengths[i], 15)  # Fotoğraf için sabit bir değer
                            else:
                                col_max_lengths[i] = max(col_max_lengths[i], len(str(cell)))

                    total_length = sum(col_max_lengths)
                    col_widths = []
                    for i, length in enumerate(col_max_lengths):
                        if total_length > 0:
                            width = (length / total_length) * page_width
                            if i == 0:  # Fotoğraf sütunu için sabit genişlik
                                col_widths.append(2 * cm)  # Fotoğraflar için daha geniş alan
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

        delete_button = QPushButton(TRANSLATIONS["delete_parameter"])
        delete_button.clicked.connect(self.delete_parameter)
        button_layout.addWidget(delete_button)

        layout.addLayout(button_layout)
        dialog.exec_()

    def add_parameter(self):
        dialog = AddParameterDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            param_name, section, param_type, combobox_file = dialog.get_data()
            if not param_name:
                QMessageBox.warning(self, "Hata", "Parametre adı boş olamaz!")
                return
            cursor = self.conn.cursor()
            cursor.execute("SELECT column_name FROM metadata WHERE column_name = ?", (param_name,))
            if cursor.fetchone():
                QMessageBox.warning(self, "Hata", "Bu parametre adı zaten mevcut!")
                return
            try:
                cursor.execute("SELECT MAX(column_order) FROM metadata")
                max_order = cursor.fetchone()[0] or 0
                cursor.execute("INSERT INTO metadata (column_name, section, type, combobox_file, column_order) VALUES (?, ?, ?, ?, ?)",
                               (param_name, section, param_type, combobox_file, max_order + 1))
                self.conn.commit()
                self.param_list.addItem(param_name)
                self.setup_inventory_tab()
                QMessageBox.information(self, "Başarılı", "Yeni parametre eklendi!")
                logging.info(f"Yeni parametre eklendi: {param_name}")
            except sqlite3.Error as e:
                logging.error(f"Parametre ekleme hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Parametre eklenemedi: {str(e)}")

    def delete_parameter(self):
        selected = self.param_list.currentItem()
        if not selected:
            QMessageBox.warning(self, "Hata", "Lütfen bir parametre seçin!")
            return
        param_name = selected.text()
        if QMessageBox.question(self, "Onay", f"'{param_name}' parametresini ve ilgili verileri silmek istediğinizden emin misiniz?",
                                QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes:
            cursor = self.conn.cursor()
            try:
                # 1. Parametrenin sırasını (column_order) al
                cursor.execute("SELECT column_order FROM metadata WHERE column_name = ?", (param_name,))
                column_order = cursor.fetchone()
                if not column_order:
                    QMessageBox.warning(self, "Hata", f"'{param_name}' parametresi bulunamadı!")
                    return
                column_index = column_order[0] - 1  # column_order 1'den başlar, indeks 0'dan

                # 2. inventory tablosundaki verileri güncelle
                cursor.execute("SELECT id, data FROM inventory")
                for row_id, data_json in cursor.fetchall():
                    data = json.loads(data_json)
                    if column_index < len(data):
                        del data[column_index]  # İlgili sütunu sil
                        cursor.execute("UPDATE inventory SET data = ? WHERE id = ?",
                                       (json.dumps(data), row_id))

                # 3. archive tablosundaki verileri güncelle
                cursor.execute("SELECT id, data FROM archive")
                for row_id, data_json in cursor.fetchall():
                    data = json.loads(data_json)
                    if column_index < len(data):
                        del data[column_index]  # İlgili sütunu sil
                        cursor.execute("UPDATE archive SET data = ? WHERE id = ?",
                                       (json.dumps(data), row_id))

                # 4. metadata tablosundan parametreyi sil
                cursor.execute("DELETE FROM metadata WHERE column_name = ?", (param_name,))

                # 5. column_order değerlerini güncelle (sıralamayı korumak için)
                cursor.execute("SELECT column_name, column_order FROM metadata ORDER BY column_order")
                rows = cursor.fetchall()
                for i, (col_name, _) in enumerate(rows, 1):
                    cursor.execute("UPDATE metadata SET column_order = ? WHERE column_name = ?",
                                   (i, col_name))

                # 6. Değişiklikleri kaydet ve arayüzü güncelle
                self.conn.commit()
                self.param_list.takeItem(self.param_list.currentRow())
                self.setup_inventory_tab()  # Formu ve tabloyu yenile
                self.load_data_from_db()    # Tabloyu güncel verilerle doldur
                self.load_archive_from_db() # Arşiv tablosunu güncelle
                QMessageBox.information(self, "Başarılı", f"'{param_name}' parametresi ve ilgili veriler silindi!")
                logging.info(f"Parametre ve verileri silindi: {param_name}")
            except sqlite3.Error as e:
                logging.error(f"Parametre silme hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Parametre silinemedi: {str(e)}")
            except Exception as e:
                logging.error(f"Genel hata: {str(e)}")
                QMessageBox.critical(self, "Hata", f"İşlem başarısız: {str(e)}")

    def manage_backups(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["backup_operations"])
        layout = QVBoxLayout(dialog)

        backup_button = QPushButton(TRANSLATIONS["manual_backup"])
        backup_button.clicked.connect(self.manual_backup)
        layout.addWidget(backup_button)

        restore_label = QLabel(TRANSLATIONS["restore_backup"])
        layout.addWidget(restore_label)

        self.backup_combo = QComboBox()
        backups = sorted(glob.glob(os.path.join(self.config["backup_path"], "inventory_backup_*.db")),
                         key=os.path.getctime, reverse=True)
        self.backup_combo.addItems([os.path.basename(b) for b in backups[:10]])
        layout.addWidget(self.backup_combo)

        restore_button = QPushButton(TRANSLATIONS["restore_item"])
        restore_button.clicked.connect(self.restore_backup)
        layout.addWidget(restore_button)

        dialog.exec_()

    def manual_backup(self):
        self.auto_backup()
        QMessageBox.information(self, "Başarılı", TRANSLATIONS["db_backed_up"])

    def auto_backup(self):
        if not os.path.exists(self.config["backup_path"]):
            os.makedirs(self.config["backup_path"])
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = os.path.join(self.config["backup_path"], f"inventory_backup_{timestamp}.db")
        try:
            shutil.copy2(DB_FILE, backup_file)
            logging.info(f"Veritabanı yedeklendi: {backup_file}")
            self.cleanup_old_backups()
        except IOError as e:
            logging.error(f"Yedekleme hatası: {str(e)}")
            QMessageBox.critical(self, "Hata", f"Yedekleme başarısız: {str(e)}")

    def cleanup_old_backups(self):
        backups = sorted(glob.glob(os.path.join(self.config["backup_path"], "inventory_backup_*.db")),
                         key=os.path.getctime)
        retention_seconds = self.config["backup_retention"] * 86400
        current_time = time.time()
        for backup in backups:
            if current_time - os.path.getctime(backup) > retention_seconds:
                try:
                    os.remove(backup)
                    logging.info(f"Eski yedek silindi: {backup}")
                except OSError as e:
                    logging.error(f"Eski yedek silme hatası: {str(e)}")

    def restore_backup(self):
        selected_backup = self.restore_combo.currentText()
        if not selected_backup:
            QMessageBox.warning(self, "Hata", "Lütfen bir yedek seçin!")
            return
        backup_path = os.path.join(self.config["backup_path"], selected_backup)
        if not os.path.exists(backup_path):
            QMessageBox.critical(self, "Hata", "Seçilen yedek dosyası bulunamadı!")
            return

        if (QMessageBox.question(self, "Onay 1", TRANSLATIONS["confirm_restore_1"],
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes and
            QMessageBox.question(self, "Onay 2", TRANSLATIONS["confirm_restore_2"],
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes and
            QMessageBox.question(self, "Son Onay", TRANSLATIONS["confirm_restore_3"],
                                 QMessageBox.Yes | QMessageBox.No) == QMessageBox.Yes):
            try:
                self.conn.close()
                shutil.copy2(backup_path, DB_FILE)
                self.conn = sqlite3.connect(DB_FILE)
                self.load_data_from_db()
                self.load_archive_from_db()
                self.setup_inventory_tab()
                QMessageBox.information(self, "Başarılı", TRANSLATIONS["restore_success"])
                logging.info(f"Yedek geri yüklendi: {backup_path}")
            except (IOError, sqlite3.Error) as e:
                logging.error(f"Yedek geri yükleme hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Yedek geri yükleme başarısız: {str(e)}")
                self.conn = sqlite3.connect(DB_FILE)

    def show_data_analysis(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["analysis_title"])
        layout = QVBoxLayout(dialog)

        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM inventory")
        data = [json.loads(row[0]) for row in cursor.fetchall()]
        headers = self.get_column_headers()

        total_label = QLabel(TRANSLATIONS["total_records"].format(len(data)))
        layout.addWidget(total_label)

        fig, axs = plt.subplots(2, 2, figsize=(10, 8))
        fig.tight_layout(pad=5.0)

        # Grup dağılımı
        group_counts = pd.Series([item[headers.index(TRANSLATIONS["group_name"])] for item in data]).value_counts()
        group_counts.plot(kind='pie', ax=axs[0, 0], autopct='%1.1f%%')
        axs[0, 0].set_title(TRANSLATIONS["group_distribution"])

        # Durum dağılımı
        status_counts = pd.Series([item[headers.index(TRANSLATIONS["status"])] for item in data]).value_counts()
        status_counts.plot(kind='bar', ax=axs[0, 1])
        axs[0, 1].set_title(TRANSLATIONS["status_distribution"])

        # Lokasyon dağılımı
        region_counts = pd.Series([item[headers.index(TRANSLATIONS["region"])] for item in data]).value_counts()
        region_counts.plot(kind='pie', ax=axs[1, 0], autopct='%1.1f%%')
        axs[1, 0].set_title(TRANSLATIONS["region_distribution"])

        # Marka dağılımı
        brand_counts = pd.Series([item[headers.index(TRANSLATIONS["brand"])] for item in data]).value_counts()
        brand_counts.plot(kind='bar', ax=axs[1, 1])
        axs[1, 1].set_title(TRANSLATIONS["brand_distribution"])

        canvas = FigureCanvas(fig)
        layout.addWidget(canvas)
        mplcursors.cursor(hover=True)
        dialog.resize(800, 600)
        dialog.exec_()

    def export_charts(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Grafikleri Kaydet", "", "PNG Dosyaları (*.png)")
        if file_name:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT data FROM inventory")
                data = [json.loads(row[0]) for row in cursor.fetchall()]
                headers = self.get_column_headers()

                fig, axs = plt.subplots(2, 2, figsize=(10, 8))
                fig.tight_layout(pad=5.0)

                group_counts = pd.Series([item[headers.index(TRANSLATIONS["group_name"])] for item in data]).value_counts()
                group_counts.plot(kind='pie', ax=axs[0, 0], autopct='%1.1f%%')
                axs[0, 0].set_title(TRANSLATIONS["group_distribution"])

                status_counts = pd.Series([item[headers.index(TRANSLATIONS["status"])] for item in data]).value_counts()
                status_counts.plot(kind='bar', ax=axs[0, 1])
                axs[0, 1].set_title(TRANSLATIONS["status_distribution"])

                region_counts = pd.Series([item[headers.index(TRANSLATIONS["region"])] for item in data]).value_counts()
                region_counts.plot(kind='pie', ax=axs[1, 0], autopct='%1.1f%%')
                axs[1, 0].set_title(TRANSLATIONS["region_distribution"])

                brand_counts = pd.Series([item[headers.index(TRANSLATIONS["brand"])] for item in data]).value_counts()
                brand_counts.plot(kind='bar', ax=axs[1, 1])
                axs[1, 1].set_title(TRANSLATIONS["brand_distribution"])

                fig.savefig(file_name, dpi=300, bbox_inches='tight')
                plt.close(fig)
                QMessageBox.information(self, "Başarılı", "Grafikler dışa aktarıldı!")
                logging.info(f"Grafikler dışa aktarıldı: {file_name}")
            except Exception as e:
                logging.error(f"Grafik dışa aktarma hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Grafik dışa aktarma başarısız: {str(e)}")

    def export_analysis_data(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Analiz Verilerini Kaydet", "", "CSV Dosyaları (*.csv)")
        if file_name:
            try:
                cursor = self.conn.cursor()
                cursor.execute("SELECT data FROM inventory")
                data = [json.loads(row[0]) for row in cursor.fetchall()]
                headers = self.get_column_headers()

                analysis_data = {
                    TRANSLATIONS["group_distribution"]: pd.Series([item[headers.index(TRANSLATIONS["group_name"])] for item in data]).value_counts().to_dict(),
                    TRANSLATIONS["status_distribution"]: pd.Series([item[headers.index(TRANSLATIONS["status"])] for item in data]).value_counts().to_dict(),
                    TRANSLATIONS["region_distribution"]: pd.Series([item[headers.index(TRANSLATIONS["region"])] for item in data]).value_counts().to_dict(),
                    TRANSLATIONS["brand_distribution"]: pd.Series([item[headers.index(TRANSLATIONS["brand"])] for item in data]).value_counts().to_dict()
                }
                df = pd.DataFrame(dict([(k, pd.Series(v)) for k, v in analysis_data.items()]))
                df.to_csv(file_name, index=False, encoding='utf-8-sig')
                QMessageBox.information(self, "Başarılı", "Analiz verileri dışa aktarıldı!")
                logging.info(f"Analiz verileri dışa aktarıldı: {file_name}")
            except Exception as e:
                logging.error(f"Analiz verisi dışa aktarma hatası: {str(e)}")
                QMessageBox.critical(self, "Hata", f"Analiz verisi dışa aktarma başarısız: {str(e)}")

    def manage_comboboxes(self):
        dialog = QDialog(self)
        dialog.setWindowTitle(TRANSLATIONS["combobox_management"])
        layout = QVBoxLayout(dialog)

        combo = QComboBox()
        options = [
            (TRANSLATIONS["edit_groups"], GROUPS_FILE, self.groups),
            (TRANSLATIONS["edit_regions"], REGIONS_FILE, self.regions),
            (TRANSLATIONS["edit_floors"], FLOORS_FILE, self.floors)
        ]
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name, combobox_file FROM metadata WHERE type = 'ComboBox' AND combobox_file IS NOT NULL")
        for column_name, file_path in cursor.fetchall():
            if file_path not in [opt[1] for opt in options]:
                options.append((column_name, file_path, self.load_json_data(file_path, [])))

        combo.addItems([opt[0] for opt in options])
        layout.addWidget(combo)

        edit_button = QPushButton(TRANSLATIONS["edit_selected_item"])
        edit_button.clicked.connect(lambda: self.edit_combobox(options[combo.currentIndex()]))
        layout.addWidget(edit_button)

        dialog.exec_()

    def edit_combobox(self, option):
        title, file_path, items = option
        dialog = ComboBoxEditDialog(self, title=title, items=items, file_path=file_path)
        dialog.exec_()

    def quick_search(self, text):
        for row in range(self.table.rowCount()):
            match = False
            for col in range(self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    match = True
                    break
            self.table.setRowHidden(row, not match)

    def filter_data(self, group):
        if group == "Tümü":
            for row in range(self.table.rowCount()):
                self.table.setRowHidden(row, False)
        else:
            group_idx = self.get_column_headers().index(TRANSLATIONS["group_name"])
            for row in range(self.table.rowCount()):
                item = self.table.item(row, group_idx)
                self.table.setRowHidden(row, item.text() != group if item else True)

    def save_current_form(self):
        logging.info("Form otomatik olarak kaydedildi.")

    def close_application(self):
        self.conn.close()
        QApplication.quit()

    def create_or_update_tables(self):
        cursor = self.conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS inventory (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT NOT NULL,
                            timestamp TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS archive (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            data TEXT NOT NULL,
                            timestamp TEXT NOT NULL)''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS metadata (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            column_name TEXT NOT NULL,
                            section TEXT NOT NULL,
                            type TEXT NOT NULL,
                            combobox_file TEXT,
                            column_order INTEGER NOT NULL)''')

        cursor.execute("SELECT column_name FROM metadata")
        existing_columns = [row[0] for row in cursor.fetchall()]
        default_columns = [
            ("Demirbaş Kodu", TRANSLATIONS["card_info"], "Metin", None, 1),
            (TRANSLATIONS["group_name"], TRANSLATIONS["card_info"], "ComboBox", GROUPS_FILE, 2),
            (TRANSLATIONS["item_name"], TRANSLATIONS["card_info"], "Metin", None, 3),
            (TRANSLATIONS["region"], TRANSLATIONS["card_info"], "ComboBox", REGIONS_FILE, 4),
            (TRANSLATIONS["floor"], TRANSLATIONS["card_info"], "ComboBox", FLOORS_FILE, 5),
            (TRANSLATIONS["quantity"], TRANSLATIONS["card_info"], "Metin", None, 6),
            ("Edinim Tarihi", TRANSLATIONS["card_info"], "Tarih", None, 7),
            (TRANSLATIONS["photo"], TRANSLATIONS["card_info"], "Metin", None, 8),
            (TRANSLATIONS["brand"], TRANSLATIONS["invoice_info"], "Metin", None, 9),
            (TRANSLATIONS["model"], TRANSLATIONS["invoice_info"], "Metin", None, 10),
            (TRANSLATIONS["invoice_no"], TRANSLATIONS["invoice_info"], "Metin", None, 11),
            ("Bağışçı", TRANSLATIONS["invoice_info"], "Metin", None, 12),
            (TRANSLATIONS["company"], TRANSLATIONS["invoice_info"], "Metin", None, 13),
            ("Özellikler", TRANSLATIONS["invoice_info"], "Metin", None, 14),
            (TRANSLATIONS["status"], TRANSLATIONS["service_info"], "Metin", None, 15),
            (TRANSLATIONS["warranty_period"], TRANSLATIONS["service_info"], "Tarih", None, 16),
            (TRANSLATIONS["description"], TRANSLATIONS["service_info"], "Metin", None, 17)
        ]

        for column_name, section, param_type, combobox_file, order in default_columns:
            if column_name not in existing_columns:
                cursor.execute("INSERT INTO metadata (column_name, section, type, combobox_file, column_order) VALUES (?, ?, ?, ?, ?)",
                               (column_name, section, param_type, combobox_file, order))
        self.conn.commit()

    def get_column_headers(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT column_name FROM metadata ORDER BY column_order")
        return [row[0] for row in cursor.fetchall()]

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = InventoryApp()
    window.show()
    sys.exit(app.exec_())
