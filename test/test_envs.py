import pytest
from tensordict import TensorDict
from torchrl.envs.utils import check_env_specs, step_mdp

from lerobot.common.envs.factory import make_env
from lerobot.common.envs.pusht import PushtEnv
from lerobot.common.envs.simxarm import SimxarmEnv


def print_spec_rollout(env):
    print("observation_spec:", env.observation_spec)
    print("action_spec:", env.action_spec)
    print("reward_spec:", env.reward_spec)
    print("done_spec:", env.done_spec)

    td = env.reset()
    print("reset tensordict", td)

    td = env.rand_step(td)
    print("random step tensordict", td)

    def simple_rollout(steps=100):
        # preallocate:
        data = TensorDict({}, [steps])
        # reset
        _data = env.reset()
        for i in range(steps):
            _data["action"] = env.action_spec.rand()
            _data = env.step(_data)
            data[i] = _data
            _data = step_mdp(_data, keep_other=True)
        return data

    print("data from rollout:", simple_rollout(100))


@pytest.mark.parametrize(
    "task,from_pixels,pixels_only",
    [
        ("lift", False, False),
        ("lift", True, False),
        ("lift", True, True),
        ("reach", False, False),
        ("reach", True, False),
        ("push", False, False),
        ("push", True, False),
        ("peg_in_box", False, False),
        ("peg_in_box", True, False),
    ],
)
def test_simxarm(task, from_pixels, pixels_only):
    env = SimxarmEnv(
        task,
        from_pixels=from_pixels,
        pixels_only=pixels_only,
        image_size=84 if from_pixels else None,
    )
    # print_spec_rollout(env)
    check_env_specs(env)


@pytest.mark.parametrize(
    "from_pixels,pixels_only",
    [
        (True, False),
    ],
)
def test_pusht(from_pixels, pixels_only):
    env = PushtEnv(
        from_pixels=from_pixels,
        pixels_only=pixels_only,
        image_size=96 if from_pixels else None,
    )
    # print_spec_rollout(env)
    check_env_specs(env)


@pytest.mark.parametrize(
    "config_name",
    [
        "default",
        "pusht",
    ],
)
def test_factory(config_name):
    import hydra
    from hydra import compose, initialize

    config_path = "../lerobot/configs"
    hydra.core.global_hydra.GlobalHydra.instance().clear()
    initialize(config_path=config_path)
    cfg = compose(config_name=config_name)

    env = make_env(cfg)

    check_env_specs(env)