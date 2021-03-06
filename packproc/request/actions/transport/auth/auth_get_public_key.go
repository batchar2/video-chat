// Получаем публичный ключ от пользователя
package auth

import (
	"fmt"
	"octopus/netpackets"
	"octopus/packproc"
	"octopus/packproc/request/flyweight"
)

type AuthGetPublicKeyProcessing struct {
	flyweight.Flyweight

	packet netpackets.TransportAuthKeyPacketHeader

	header netpackets.PacketHeader
	// Сохранить публичный ключ клиента
	SaveClientPublicKeyAction packproc.CallbackSetDataAction
}

func (self *AuthGetPublicKeyProcessing) Processing(data []byte) bool {

	fmt.Println("AuthGetPublicKeyProcessing")
	self.packet = netpackets.TransportAuthKeyPacketHeader{}
	if err := self.packet.ParseBinaryData(data); err {
		return true
	}

	self.header = netpackets.PacketHeader{}
	self.header.SetMagicNumber(self.packet.GetMagicNumber())
	self.header.SetPacketType(self.packet.GetPacketType())

	self.SaveClientPublicKeyAction(self.packet.GetKey(), self.packet.GetKeyLenght())

	return false
}

func (self *AuthGetPublicKeyProcessing) GetData2PacketHeader() *netpackets.PacketHeader {
	return &self.header

}

func (self *AuthGetPublicKeyProcessing) GetBodyBinaryData() []byte {
	return nil
}

func (self *AuthGetPublicKeyProcessing) BinaryData() []byte {
	return self.packet.Binary()
}
