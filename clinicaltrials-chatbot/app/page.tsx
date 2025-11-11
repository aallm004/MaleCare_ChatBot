import { Card, CardContent } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Button } from "@/components/ui/button"

export default function ChatBox() {
  return (
    <Card className="max-w-md mx-auto p-4 space-y-4">
      <CardContent className="h-96 overflow-y-auto space-y-2">
        <div className="bg-red-300 p-2 rounded-2xl self-start w-fit">Hello! How can I help you?</div>
        <div className="bg-blue-100 p-2 rounded-2xl self-end w-fit">Find trials for breast cancer</div>
      </CardContent>
      <form className="flex gap-2">
        <Input placeholder="Ask about a clinical trial..." />
        <Button type="submit">Send</Button>
      </form>
    </Card>
  )
}
