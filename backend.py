import requests
import pandas as pd

def download_and_convert_yandex_xlsx(url_file, xlsx_path, csv_path):
    # Шаг 1: Получаем прямую ссылку на файл
    api_url = "https://cloud-api.yandex.net/v1/disk/public/resources/download"
    params = {"public_key": url_file}
    response = requests.get(api_url, params=params)
    response.raise_for_status()

    download_url = response.json()["href"]

    # Шаг 2: Скачиваем файл
    with requests.get(download_url, stream=True) as r:
        r.raise_for_status()
        with open(xlsx_path, "wb") as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    print(f"Скачано: {xlsx_path}")

    # Шаг 3: Конвертируем в CSV
    df = pd.read_excel(xlsx_path)
    df.to_csv(csv_path, index=False, encoding='utf-8-sig')
    print(f"Преобразовано в CSV: {csv_path}")


def update_data():
    with open("day_url") as f:
        download_and_convert_yandex_xlsx(
            url_file=f.read(),
            xlsx_path="day.xlsx",
            csv_path="day.csv"
        )
    with open("all_url") as f:
        download_and_convert_yandex_xlsx(
            url_file=f.read(),
            xlsx_path="all.xlsx",
            csv_path="all.csv"
        )


if __name__ == "__main__":
    update_data()
