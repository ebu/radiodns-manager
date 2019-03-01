def test_actor_has_started(setup_db, actor_setup):
    assert actor_setup.spi_generator_actor.is_alive() is True
