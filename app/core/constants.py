from models import CourierType

salary_coefficients = {
    CourierType.AUTO: 4,
    CourierType.BIKE: 3,
    CourierType.FOOT: 2,
}

rating_coefficients = {
    CourierType.AUTO: 1,
    CourierType.BIKE: 2,
    CourierType.FOOT: 3,
}

courier_type_settings = {
    CourierType.FOOT: {
        "max_weight": 10,
        "max_orders": 2,
        "max_regions": 1,
        "order_time": [25, 10],
        "delivery_cost": [1.0, 0.8],
    },
    CourierType.BIKE: {
        "max_weight": 20,
        "max_orders": 4,
        "max_regions": 2,
        "order_time": [12, 8],
        "delivery_cost": [1.0, 0.8],
    },
    CourierType.AUTO: {
        "max_weight": 40,
        "max_orders": 7,
        "max_regions": 3,
        "order_time": [8, 4],
        "delivery_cost": [1.0, 0.8],
    },
}
