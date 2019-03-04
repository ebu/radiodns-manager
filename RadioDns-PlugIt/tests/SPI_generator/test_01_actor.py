def test_actor_has_started(setup_db, actor_setup):
    assert actor_setup.spi_generator_actor.is_alive() is True


def test_actor_can_be_restarted_on_demand(setup_db, actor_setup):
    actor_setup.stop()
    assert actor_setup.spi_generator_actor.is_alive() is False
    actor_setup.tell_to_actor({"type": "test_msg"})
    assert actor_setup.spi_generator_actor.is_alive() is True
