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

courier_settings = {
    CourierType.FOOT: {
        "max_weight": 10,
        "max_orders": 2,
        "max_regions": 1,
        "first_order_time": 25,
        "next_order_time": 10,
        "next_delivery_cost": 0.8,
    },
    CourierType.BIKE: {
        "max_weight": 20,
        "max_orders": 4,
        "max_regions": 2,
        "first_order_time": 12,
        "next_order_time": 8,
        "next_delivery_cost": 0.8,
    },
    CourierType.AUTO: {
        "max_weight": 40,
        "max_orders": 7,
        "max_regions": 3,
        "first_order_time": 8,
        "next_order_time": 4,
        "next_delivery_cost": 0.8,
    },
}
