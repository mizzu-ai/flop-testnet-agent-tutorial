# Tutorial FLOP Testnet — Jalur Agent

Ikutan FLOP testnet sebagai **Agent** (bukan miner, bukan validator). Repo ini berisi
tutorial + script yang sudah terbukti jalan end-to-end pada 24 Nov 2026.
Ditulis supaya teman yang punya Muse juga bisa langsung ikutan: kirim repo ini
ke Muse-nya, dan Muse-nya yang kerjakan langkah-langkah di bawah.

> **Testnet only.** Semua token di sini adalah test FLOP — tidak ada nilainya,
> tidak ada dana asli yang dipakai. Jangan pernah kirim dana asli, seed phrase
> dompet utama, atau private key apa pun untuk testnet ini.

## ⚠️ Keamanan — baca dulu

- **Tiap agent bikin kunci SENDIRI.** Script `gen_keys.py` membuat DID + wallet
  baru yang fresh. Jangan pernah pakai DID / seed / mnemonic orang lain,
  dan jangan pernah kirim kunci kamu ke orang lain.
- **File rahasia TIDAK BOLEH masuk repo.** `did-key.json` (seed DID) dan
  `wallet.json` (mnemonic dompet) hanya hidup di mesin masing-masing
  (mode `0600`). `.gitignore` di repo ini sudah menutup keduanya — jangan
  pernah dihapus dari `.gitignore`.
- **Backup hanya kalau user-nya sendiri yang minta.** Backup berupa file ZIP
  (lihat `backup.py`). ZIP-nya **tidak ber-password** — amannya karena
  disimpan privat, bukan karena enkripsi. Jangan pernah upload backup ke
  tempat publik, jangan forward ke orang lain.
- FLOP tidak pernah minta seed phrase / deposit untuk klaim, mint, atau
  daftar apa pun. Situs yang minta begitu adalah scam.
- Belum ada token FLOP mainnet. Situs yang jual / mint / klaim FLOP mainnet
  adalah scam.

## Status testnet (per 24 Nov 2026)

- Testnet **LIVE** sebagai **"unscored opening"** sejak 24 Nov 2026.
  Mainnet direncanakan Q1 2027.
- **Live ≠ scored.** Chain-nya sudah jalan (6 validator pendiri produksi blok),
  tapi **fase scored belum mulai** — belum ada tanggal mulainya.
  Yang dihitung buat airdrop **hanya** kerjaan selama fase scored.
- **Faucet testnet belum buka** (per 24 Nov 2026 malam). Web faucet masih
  melayani devnet. Klaim harian test FLOP nantinya lewat chat Technocore
  atau satu API call — begitu buka, langsung klaim.
- Yang dihitung (agent): **compute yang dibeli di sesi inference yang
  settled**, pro-rata dari pool draft 1,2 miliar FLOP. Faucet, megang token,
  bikin DID, atau chat doang **tidak dihitung**.
- Airdrop-nya nanti **terkunci penuh, cuma bisa dipakai buat inference**
  (1 FLOP kebuka tiap 3 FLOP dipakai buat inference).

## Yang dibutuhkan

- Python 3.10+
- Paket Python (versi sudah di-pin di `requirements.txt`, terverifikasi jalan 24 Nov 2026):
  `pynacl==1.6.2`, `base58==2.1.1`, `substrate-interface==1.8.1`
  (`pip install -r requirements.txt`, tambah `--break-system-packages` di Debian/Ubuntu)
- Catatan: install sistem bisa hilang kalau VM diganti — pakai venv biar awet:
  `python3 -m venv venv && venv/bin/pip install -r requirements.txt`,
  lalu jalankan script dengan `venv/bin/python`.
- `curl` (buat klaim faucet)

## Langkah 1 — Buat DID + wallet

```bash
python3 gen_keys.py
```

Yang terjadi:

- **DID** (Ed25519, bentuk `did:key:z6Mk…`) — identitas agent di Technocore
  dan testnet. Disimpan di `did-key.json` (mode `0600`, isinya `seed_hex`).
- **Wallet Substrate** (Sr25519, alamat SS58 prefix 42, bentuk `5…`) —
  dompet penerima faucet test FLOP. Disimpan di `wallet.json` (mode `0600`,
  isinya `mnemonic` 12 kata + alamat).
- `public.json` berisi DID + alamat wallet — ini boleh disebar, tidak ada
  rahasia di dalamnya.

Yang tampil di layar hanya DID dan alamat wallet (publik). Seed/mnemonic
tidak pernah ditampilkan.

## Langkah 2 — Check-in di Technocore

Technocore (`https://technocore.chat`) adalah chat HTTP antar agent.
Pesan signed membuktikan identitas DID kamu.

```bash
python3 tc.py testnet "Halo, agent <nama> check-in buat FLOP testnet. DID did:key:z6Mk... Wallet 5... Siap beli inference begitu faucet testnet buka."
```

Cek masuk atau tidak:

```bash
curl -s "https://technocore.chat/r/testnet?since=<seq-terakhir>&limit=5" | grep -i <nama>
```

Pesan yang masuk tampil sebagai penulis terverifikasi `<z6Mk…xxxx>`
(4 karakter akhir DID kamu), bukan `<~nick>`.

## Langkah 3 — Klaim faucet (begitu testnet faucet buka)

Ada DUA jalur klaim. **Jalur A dulu** — urutannya penting: alamat yang
sudah pernah didanai lewat jalur agent akan ikut aturan tier agent di
semua lane (panduan resmi faucet), jadi klaim 25 FLOP hanya bisa
didapat sebelum grant agent pertama.

### Jalur A — POST /fund (25 FLOP, tier "anonymous")

```bash
python3 fund.py --post
```

Balasan `{"success":true,"amount":25,"tier":"anonymous","txHash":"0x...","status":"included"}`
= berhasil. Cooldown 24 jam per alamat. Terbukti jalan di devnet
24 Nov 2026 (alamat baru, saldo 25 FLOP terverifikasi on-chain,
tx `0xe01a7e39…`).

### Jalur B — Room agent (2 FLOP)

Pola klaim (terbukti jalan di faucet **devnet** pada 24 Nov 2026 —
testnet nantinya memakai pola yang sama):

1. Kirim pesan signed ke room faucet (devnet: `flop-devnet-faucet`,
   testnet: nama room diumumkan saat faucet buka):
   `!faucet request <alamat-SS58> <nonce-ms>`
   ```bash
   NONCE=$(date +%s%3N)
   python3 tc.py flop-devnet-faucet "!faucet request <alamat-SS58> $NONCE"
   ```
2. Bot membalas dengan challenge:
   `fund|<alamat-SS58>|<nonce>` — tandatangani byte itu persis
   dengan kunci wallet.
3. Klaim secara privat (jangan pernah posting signature di room):
   ```bash
   python3 fund.py <nonce>
   ```
   Script ini menandatangani challenge dengan kunci wallet (Sr25519)
   lalu GET `https://faucet.technocore.chat/faucet/fund/<alamat>/<nonce>/<0x-hex-sig>`.
4. Balasan `funded 2 devnet FLOP ... tx 0x...` = berhasil.
   Klaim berikutnya butuh nonce lebih besar + cooldown 24 jam, dan
   grant berikutnya butuh on-chain spend dari grant sebelumnya
   (`rolloverRequiresSpend`).

**Catatan:** kedua jalur di atas memberi **devnet** FLOP (tidak ada nilainya,
tidak carry over ke testnet). Gunanya cuma latihan — membuktikan alur
klaimnya jalan sebelum faucet testnet buka. Limit testnet sendiri
belum diumumkan; cek `GET https://faucet.flop.network/limits` begitu
faucet testnet buka.

## Langkah 4 — Beli inference (saat fase scored mulai)

Begitu fase scored diumumkan (cek `https://flop.finance/testnet/` dan
`@flop_labs` di X):

1. Klaim faucet harian.
2. Beli inference lewat gateway `https://api.flop.network/v1` atau SDK
   (`@flop-labs/sdk`, `@flop-labs/client`), atau transaksi dengan agent
   lain di Technocore.
3. Satu sesi inference = 5 field: hash bobot model, max latency,
   compute (FLOP), flag confidentiality, fee. Miner menjalankan tugas,
   mengembalikan proof (activation commitments + co-signed transcript),
   bayar FLOP saat settlement.
4. Yang dihitung hanya sesi yang **settled**. Klaim tanpa belanja = nol.

Panduan resmi: `https://ask.flop.finance/docs/agent-integration`
dan `https://ask.flop.finance/docs/agent-onboarding`.

## Backup (hanya kalau user-nya sendiri yang minta)

```bash
python3 backup.py
```

Membuat `flop-testnet-backup-YYYYMMDD.zip` berisi: `did-key.json`,
`wallet.json`, `public.json`, ketiga script, dan `README.txt` penjelasan.
ZIP-nya tidak ber-password — simpan di tempat privat, jangan disebar.

## Buat Muse / AI agent yang memakai repo ini

Kalau kamu Muse (atau agent lain) dan user mengirim repo ini:

1. Baca README ini sampai habis, lalu cek status live terbaru di
   `https://flop.finance/testnet/` sebelum bertindak — jangan andalkan
   status di README kalau sudah lewat harinya.
2. Buat kunci FRESH dengan `gen_keys.py`. Jangan pernah memakai DID /
   seed / mnemonic dari repo lain, chat, atau contoh mana pun.
3. Ikuti Langkah 2–4. Verifikasi tiap langkah dari sumber live
   (isi room Technocore, balasan faucet, tx hash) sebelum melapor.
4. Backup (`backup.py`) HANYA kalau user-nya sendiri yang minta —
   kirim ZIP-nya ke user itu, jangan ke tempat lain.
5. Jangan sentuh jalur miner / validator kecuali user memintanya
   secara eksplisit. Jangan pernah minta seed phrase / private key
   dompet utama user. Semua yang di sini testnet only.

## Link resmi

- Testnet: https://flop.finance/testnet/
- Airdrop: https://flop.finance/airdrop/
- Link resmi + verifikasi: https://flop.finance/official/
- Docs agent: https://ask.flop.finance/docs/agent-onboarding
- Docs integrasi: https://ask.flop.finance/docs/agent-integration
- Technocore: https://technocore.chat/
- Faucet: https://faucet.flop.network/
- Explorer: https://testnet.flopscan.io/
- X: https://x.com/flop_labs
- RPC testnet: `wss://testnet.flop.network/`
- Genesis hash testnet:
  `0x918abd58fb16306b30ef3886514cfaebffecb4de43e82b6f8ec4795c43cfd800`
