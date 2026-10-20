from inventory_api.store import InventoryStore


def test_read_operations_do_not_expose_store_state():
    store = InventoryStore([])

    created = store.add({"product_name": "Rice"})
    created["product_name"] = "Changed outside the store"

    assert store.get(created["id"])["product_name"] == "Rice"

    items = store.all()
    items[0]["stock"] = 99
    assert store.get(created["id"])["stock"] == 0