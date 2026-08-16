# 🚀 MPC Clipper - Hızlı Kurulum & Kullanım Rehberi

Bu rehber, **MPC Clipper** yazılımını bilgisayarınıza sıfırdan kurup kullanabilmeniz için gerekli tüm adımları içermektedir.

---

## 📥 1. Gerekli Programların İndirme Bağlantıları

| Program | Açıklama | İndirme Linki |
| :--- | :--- | :--- |
| **Python 3.x** | Uygulamayı çalıştırmak için gereklidir. | 🔗 [Python İndir (Resmi)](https://www.python.org/downloads/) |
| **MPC-HC** *(Önerilen)* | Zaman kodlarını alacağımız video oynatıcı. | 🔗 [MPC-HC İndir (GitHub Releases)](https://github.com/clsid2/mpc-hc/releases) |
| **MPC-BE** *(Alternatif)* | Alternatif video oynatıcı. | 🔗 [MPC-BE İndir (SourceForge)](https://sourceforge.net/projects/mpcbe/) |
| **FFmpeg** | Video kesme ve birleştirme motoru. | 🔗 [FFmpeg İndir (Builds)](https://github.com/BtbN/FFmpeg-Builds/releases) |

---

## ⚙️ 2. Adım Adım Kurulum Adımları

### Adım 1: Python'ı Yükleyin
1. Yukarıdaki linkten **Python** kurucusunu indirin.
2. Kurulum ekranı açıldığında **en altta yer alan `Add Python.exe to PATH`** seçeneğini **İŞARETLEYİN**.
3. **Install Now** butonuna basarak kurulumu tamamlayın.

### Adım 2: MPC-HC / MPC-BE Web Arayüzünü Açın
MPC Clipper'ın video oynatıcınızla haberleşebilmesi için bu ayar zorunludur:
1. **MPC-HC** (veya MPC-BE) uygulamasını açın.
2. Klavyeden **`O`** tuşuna basarak **Seçenekler (Options)** penceresini açın.
3. Sol menüden **Oynatıcı ➔ Web Arayüzü** sekmesine girin.
4. **"Dinleme Portu" (Listen on port)** kutusunu işaretleyin ve port değerinin **`13579`** olduğundan emin olun.
5. **Uygula** ve **Tamam** butonlarına tıklayın.

### Adım 3: FFmpeg Dosyalarını Yerleştirin
1. İndirdiğiniz FFmpeg `.zip` dosyasını bir klasöre çıkarın.
2. İçindeki `bin` klasöründe yer alan **`ffmpeg.exe`** ve **`ffprobe.exe`** dosyalarını kopyalayın.
3. Bu iki dosyayı **`mpc_clipper.pyw`** dosyasının bulunduğu ana klasöre yapıştırın.

---

## 🎬 3. Video Kesme ve Birleştirme Adımları

1. Videonuzu **MPC-HC** oynatıcısında açın.
2. **MPC Clipper** uygulamasını çalıştırmak için **`mpc_clipper.pyw`** dosyasına çift tıklayın.
3. Videoda kesmek istediğiniz ilk parçanın başlangıç noktasına gelin:
   - MPC Clipper üzerindeki **`Set Start (from MPC)`** butonuna basın.
4. Bitiş noktasına gelin:
   - **`Set End (from MPC)`** butonuna basın.
5. **`Add Clip to List ⬇️`** butonuna basarak klibi listeye ekleyin.
6. Tüm kliplerinizi ekledikten sonra:
   - Donmasız ve senkronize sonuç için **"Yeniden Kodla (Kesin Senkronize)"** modunu seçili bırakın.
   - **`Extract & Combine All ✂️`** butonuna basarak videonuzu kaydedin!
