from agents.profile import load_profile, mark_seen, mark_weak

mark_seen("ishita", "attention")
mark_seen("ishita", "attention")
mark_weak("ishita", "graphrag")
print(load_profile("ishita"))   # predict this
print(load_profile("nobody"))   # predict this