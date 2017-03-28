import ctypes
import logging

from abc import ABC, abstractmethod


from .packets.chanell_level import (ChanelLevelPacket, BaseChanelLevelPacket, ChanelLevelPacketKeyAuth, ChanelLevelPacketUserAuth)
from .packets import default_options as op

"""
Реализуется паттерн "Фабричный метод", для идентификации принятых пакетов.
Продуктами являются пакеты, описанные в chanell_level.py
"""


class PacketCreator(ABC):
    """ Базовый класс создателя продукта """
    @abstractmethod
    def factory_method(self, data):
        """ Фабричный метод, приводит набор данных к соответствующей струтуре
        :param data: данные, полученые от пользователя 
        """
        pass


class PacketCreatorNormal(PacketCreator):
    """  Создатель "нормального пакета" """
    
    def factory_method(self, data):
        logging.error('Пакет определен как CHANEL_PACKET_TYPE_NORMAL')
        return ChanelLevelPacket.from_buffer_copy(data)


class PacketCreatorClientSendPublicKey(PacketCreator):
    """  Клиент подключается и высылает свой публичный ключ """
    
    def factory_method(self, data):
        logging.error('Пакет определен как CHANEL_PACKET_TYPE_PUBLIC_KEY_СLIENT_SERVER_EXCHANGE')
        return ChanelLevelPacketKeyAuth.from_buffer_copy(data)


class PacketCreatorServerSendPublicKey(PacketCreator):
    """  В ответ сервер высылает свой публичный ключ  """
    
    def factory_method(self, data):
        logging.error('Пакет определен как CHANEL_PACKET_TYPE_PUBLIC_KEY_SERVER_CLIENT_EXCHANGE')
        return ChanelLevelPacketKeyAuth.from_buffer_copy(data)


class PacketCreatorQOS(PacketCreator):
    """ Создатель пакета QOS  """
    
    def factory_method(self, data):
        return ChanelLevelPacket.from_buffer_copy(data)


class ChanelPacketCreator:
    """  Интерфейс, определяющий конструирование пакетов. Работа производится через него. Некий фасад  """
    
    _packets_creators = {}
    
    def addAction(self, *, packet_type, concrete_factory, cmd):
        """ Сопоставляем тип пакета, "построитель пакета" и обработчик информации
        :param packet_type: тип, пакета
        :param concrete_factory: фабричный метод, ответственный за пакет
        :param cmd: команда, которой передается пакет для обработки
        """
        self._packets_creators[packet_type] = {
            'factory': concrete_factory,
            'cmd': cmd,
        }


    def make_packet_chanel(self, data):
        """ По данным полученым из сети строится соответствующий сетевой пакет 
        :param data: данные, полученые по сети
        """
        try:
            # выполняем преобразование данных в пакет БАЗОВОГО ФОРМАТА, для идентификации
            packet = BaseChanelLevelPacket.from_buffer_copy(data)
        except Exception as e:
            logging.error(str(e))
            return None

        if packet is not None:
            logging.error('Получен пакет размера: {0} байт'.format(ctypes.sizeof(packet)))
            if op.MAGIC_NUMBER == packet.magic_number:
                # Идентифицируем пакет
                if packet.type in self._packets_creators:
                    factory = self._packets_creators[packet.type]['factory']
                    cmd = self._packets_creators[packet.type]['cmd']
                    # Вызываем обработчик и передаем ему "распарсеный" пакет
                    return cmd(packet=factory.factory_method(data))
                else:
                    logging.error('Пакет неизвестного типа!')
            else:
                logging.error('Пакет не имеет магического числа!')
        else:
             logging.error('Пакет не распарсился')
        return None