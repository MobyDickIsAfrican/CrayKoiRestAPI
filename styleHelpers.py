# helper functions for modifying data before being saved

def getStyle(comp):
    data = {}
    try:
        data.update(comp)
        data.pop("left")
        data.pop("top")
        data.pop("height")
        data.pop("width")
        data.pop("parent")
        data.pop("id")
        return data
    except KeyError:
        raise KeyError

def getComp(comp):
    data = {}
    data["left"] = comp["left"]
    data["top"] = comp["top"]
    data["height"] = comp["height"]
    data["width"] = comp["width"]
    data["parent"] = comp["parent"]
    data["comp_id"] = comp["id"]
    return data