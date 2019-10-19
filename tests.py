from engine import Engine


class Members(Engine):
    # 存储列表
    save_list = ['memcache', 'redis']
    # sign_key: 如果需要更新该 model的所有cache 在model定义中修改 sign_key 即可
    sign_key = "Members"

    def __init__(self, uid):
        Engine.__init__(self)
        self.id = uid  # model.pk
        self.data = {}  # 数据

    @classmethod
    def get(cls, uid, time_out=None):
        obj = super(Members, cls).get(str(uid))
        if not obj:
            obj = cls._install(uid)

        return obj

    @classmethod
    def _install(cls, uid):
        """
        缓存为空时 与数据库同步数据
        """
        member = cls(uid)
        # 同步数据
        # member.data = xxx
        member.put()

        return member
