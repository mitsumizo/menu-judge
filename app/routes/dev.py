"""Development routes for UI testing.

These routes are only available in development mode (FLASK_DEBUG=1).
"""

from flask import Blueprint, render_template

from app.models.dish import BoundingBox, Category, Dish

dev_bp = Blueprint("dev", __name__, url_prefix="/dev")


def get_mock_dishes() -> list[Dish]:
    """Generate mock dish data for UI testing."""
    return [
        Dish(
            original_name="Fresh green papaya achar",
            translated_name="フレッシュグリーンパパイヤアチャール",
            description="スリランカ風ピクルス。グリーンパパイヤ、プルーン、早生赤を使った前菜",
            spiciness=2,
            sweetness=3,
            ingredients=["グリーンパパイヤ", "プルーン", "早生赤"],
            allergens=[],
            category=Category.APPETIZER,
            bounding_box=BoundingBox(x=0.05, y=0.05, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Shredded beetroot salad",
            translated_name="シュレッドビートルートサラダ",
            description="マリネしたビーツにジンジャーとカルダモンを加えた爽やかなサラダ",
            spiciness=1,
            sweetness=2,
            ingredients=["ビーツ", "ショウガ", "カルダモン"],
            allergens=[],
            category=Category.APPETIZER,
            bounding_box=BoundingBox(x=0.35, y=0.05, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Sri Lankan Ala thel dala",
            translated_name="スリランカアラテルダラ",
            description="スリランカの伝統的なスパイス風味のポテトサラダ。温かいポテトサラダスタイル",
            spiciness=3,
            sweetness=1,
            ingredients=["ポテト", "スパイス"],
            allergens=[],
            category=Category.APPETIZER,
            bounding_box=BoundingBox(x=0.65, y=0.05, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Papad with chopped salad",
            translated_name="パパドと刻みサラダ",
            description="ウルド豆粉で作った揚げせんべいに刻み野菜とモルディブ風魚をトッピング",
            spiciness=1,
            sweetness=1,
            ingredients=["パパド", "野菜", "モルディブフィッシュ"],
            allergens=["魚"],
            category=Category.APPETIZER,
            bounding_box=BoundingBox(x=0.05, y=0.25, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Roti with sauteed mung beans",
            translated_name="ロティと炒めたムング豆",
            description="スパイス入りの薄い生地に緑豆とコリアンダーのテンパラードを添えた一品",
            spiciness=2,
            sweetness=1,
            ingredients=["ロティ", "ムング豆", "コリアンダー"],
            allergens=["グルテン"],
            category=Category.APPETIZER,
            bounding_box=BoundingBox(x=0.35, y=0.25, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Fresh raw tuna tartare",
            translated_name="フレッシュ生マグロのタルタル",
            description="名古屋市中央市場から仕入れた新鮮なマグロにガラムマサラアイオリとブラックパウダーをあしらったタルタル",
            spiciness=1,
            sweetness=1,
            ingredients=["マグロ", "ガラムマサラ", "アイオリ"],
            allergens=["魚", "卵"],
            category=Category.APPETIZER,
            bounding_box=BoundingBox(x=0.65, y=0.25, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Lamb Kottu Roti",
            translated_name="ラムコットゥロティ",
            description="スリランカの代表的なストリートフード。ラム肉と野菜を刻んだロティと炒めた一品",
            spiciness=4,
            sweetness=1,
            ingredients=["ラム肉", "ロティ", "野菜", "スパイス"],
            allergens=["グルテン"],
            category=Category.MAIN,
            bounding_box=BoundingBox(x=0.05, y=0.45, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Black Pork Curry",
            translated_name="ブラックポークカレー",
            description="ローストしたスパイスで作る濃厚な黒カレー。豚肉をじっくり煮込んだスリランカの伝統料理",
            spiciness=5,
            sweetness=2,
            ingredients=["豚肉", "ローストスパイス", "ココナッツ"],
            allergens=[],
            category=Category.MAIN,
            bounding_box=BoundingBox(x=0.35, y=0.45, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Watalappan",
            translated_name="ワタラッパン",
            description="スリランカの伝統的なココナッツミルクプリン。ジャガリーとカルダモンの香り",
            spiciness=1,
            sweetness=5,
            ingredients=["ココナッツミルク", "ジャガリー", "カルダモン", "卵"],
            allergens=["卵"],
            category=Category.DESSERT,
            bounding_box=BoundingBox(x=0.65, y=0.45, width=0.25, height=0.15),
        ),
        Dish(
            original_name="Ceylon Tea",
            translated_name="セイロンティー",
            description="スリランカ産の高品質な紅茶。ミルクと砂糖を添えて",
            spiciness=1,
            sweetness=3,
            ingredients=["紅茶", "ミルク", "砂糖"],
            allergens=["乳"],
            category=Category.BEVERAGE,
            bounding_box=BoundingBox(x=0.05, y=0.65, width=0.25, height=0.15),
        ),
    ]


@dev_bp.route("/mock-results")
def mock_results():
    """Render mock dish results for UI testing."""
    dishes = get_mock_dishes()
    return render_template(
        "partials/dish_list.html",
        dishes=dishes,
        provider="mock",
        processing_time=0.0,
    )


@dev_bp.route("/mock-page")
def mock_page():
    """Render full page with mock results for UI testing."""
    dishes = get_mock_dishes()
    return render_template(
        "dev/mock_page.html",
        dishes=dishes,
        provider="mock",
        processing_time=0.0,
    )
