CREATE TABLE properties (
  id INT AUTO_INCREMENT PRIMARY KEY,
  listing_id INT UNIQUE NOT NULL, -- 楽待上の一意ID（URLやクエリパラメータから抽出）
  address TEXT, -- 住所
  pub_date DATE, -- 登録日
  access TEXT, -- 最寄駅やアクセス情報
  structure VARCHAR(46), -- 木造 / RC造 など
  land_area INT, -- 土地面積（平米）
  building_area INT, -- 建物面積（平米）
  build_at DATE, -- 築年月（西暦）
  floors INT, -- 階数（例: 3階建）
  detail_url TEXT, -- 物件のURL
  scraped_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP, -- 初回取得日時
  closed_at DATE -- 楽待に掲載されなくなった日付
);

CREATE TABLE price_history (
  id INT AUTO_INCREMENT PRIMARY KEY,
  property_id INT NOT NULL,
  price INT NOT NULL, -- 価格
  gross DECIMAL(5,2), -- 利回り（例: 8.25% は 8.25）
  scraped_at DATETIME NOT NULL, -- 価格取得日時（時系列分析用）
  FOREIGN KEY (property_id) REFERENCES properties(id) ON DELETE CASCADE
);