import { UserCircleIcon } from '@heroicons/react/24/solid'
import { useRef, useState, useEffect } from 'react'
import { toast } from 'sonner'
import { Save } from "lucide-react"

export default function Profile() {

    const fileInputRef = useRef(null)
    const [avatar, setAvatar] = useState(null)

    const [form, setForm] = useState({
        username: '',
        firstName: '',
        middleName: '',
        lastName: '',
        phone: '',
        email: '',
        birthDate: '',
        gender: '',
    })

    useEffect(() => {
        const savedAvatar = localStorage.getItem("userAvatar")
        if (savedAvatar) setAvatar(savedAvatar)
    }, [])

    const handleImageChange = (e) => {
        const file = e.target.files[0]
        if (!file) return

        const reader = new FileReader()
        reader.onloadend = () => {
            setAvatar(reader.result)
            localStorage.setItem("userAvatar", reader.result)
        }
        reader.readAsDataURL(file)
    }

    const handleChange = (key, value) => {
        setForm({ ...form, [key]: value })
    }

    const handleSave = (e) => {
        e.preventDefault()
        if (!form.firstName || !form.email) {
            toast.error("First Name and Email are required!")
            return
        }

        localStorage.setItem("userProfile", JSON.stringify(form))
        toast.success("Profile saved successfully!")
    }

    const inputClass = "block w-full mt-1 rounded-md bg-inputBckground px-3 py-1.5 text-base text-[muted-foreground] placeholder:text-[muted-foreground] focus:outline-none focus:ring-2 focus:ring-[#0DCCF2]";
    return (
        <div className="flex flex-col items-center justify-center min-h-screen p-4 bg-background">
            <div className="w-full max-w-3xl my-3 ">
                <h1 className="text-2xl font-bold text-foreground">Profile</h1>
                <p className="mt-1 text-md text-muted-foreground">
                    Manage your account information
                </p>
            </div>
            <form className="w-full max-w-3xl p-6 mt-5 rounded-2xl bg-subBackground border border-[muted-foreground] space-y-6">
                <div className="space-y-12">
                    {/* Avatar */}
                    <div className="col-span-full ">
                        <label className="block text-sm font-medium text-foreground ">
                            Photo
                        </label>
                        <div className="mt-2 flex items-center gap-x-3 mb-5">
                            {avatar ? (
                                <img src={avatar} className="w-16 h-16 rounded-full object-cover" />
                            ) : (
                                <UserCircleIcon className="w-16 h-16 text-gray-500" />
                            )}
                            <button type="button" onClick={() => fileInputRef.current.click()} className="bg-buttonBackground px-5 py-2 rounded-xl text-sm font-semibold text-logoColor focus:outline-none focus:ring-2 focus:ring-[#0DCCF2] focus:ring-offset-0 hover:outline-none hover:ring-2 hover:ring-[#0DCCF2] hover:ring-offset-0">
                                Change
                            </button>
                            <input type="file" accept="image/*" ref={fileInputRef} onChange={handleImageChange} className="hidden" />
                        </div>
                    </div>

                    {/* Personal Info */}
                    <div className="grid grid-cols-1 sm:grid-cols-6 gap-6">
                        <div className="sm:col-span-3">
                            <label className="block text-sm font-medium text-foreground">First Name *</label>
                            <input
                                type="text"
                                value={form.firstName}
                                onChange={(e) => handleChange('firstName', e.target.value)}
                                className={inputClass}
                                placeholder='Mayar'
                                required
                            />
                        </div>
                        <div className="sm:col-span-3">
                            <label className="block text-sm font-medium text-foreground">Email *</label>
                            <input
                                type="email"
                                value={form.email}
                                onChange={(e) => handleChange('email', e.target.value)}
                                className={inputClass}
                                placeholder='mayaribrahim@gmail.com'
                                required
                            />
                        </div>
                        <div className="sm:col-span-3">
                            <label className="block text-sm font-medium text-foreground">Midlle Name</label>
                            <input type="text" value={form.middleName} placeholder='Ibrahim' onChange={(e) => handleChange('middleName', e.target.value)} className={inputClass} />
                        </div>
                        <div className="sm:col-span-3">
                            <label className="block text-sm font-medium text-foreground">Last Name</label>
                            <input type="text" value={form.lastName} placeholder='Fathy' onChange={(e) => handleChange('lastName', e.target.value)} className={inputClass} />
                        </div>
                        <div className="sm:col-span-3">
                            <label className="block text-sm font-medium text-foreground">Username</label>
                            <input type="text" value={form.username} placeholder='mayar_ibrahim' onChange={(e) => handleChange('username', e.target.value)} className={inputClass} />
                        </div>
                        <div className="sm:col-span-3">
                            <label className="block text-sm font-medium text-white">Phone</label>
                            <input type="tel" value={form.phone} placeholder='012 xxxxxxxx' onChange={(e) => handleChange('phone', e.target.value)} className={inputClass} />
                        </div>
                        <div className="sm:col-span-3">
                            <label className="block text-sm font-medium text-foreground">Birth Date</label>
                            <input type="date" value={form.birthDate} placeholder='15/2/2005' onChange={(e) => handleChange('birthDate', e.target.value)} className={inputClass} />
                        </div>

                        <div className="sm:col-span-4">
                            <label className="block text-sm/6 font-medium text-foreground mb-2">
                                Gender
                            </label>

                            <div className="flex items-center gap-x-6">
                                <label className="flex items-center gap-x-2 text-sm text-foreground">
                                    <input
                                        type="radio"
                                        name="gender"
                                        value="male"
                                        checked={form.gender === "male"}
                                        onChange={(e) => handleChange("gender", e.target.value)}
                                        className="accent-[#0DCCF2]"
                                    />
                                    Male
                                </label>

                                <label className="flex items-center gap-x-2 text-sm text-foreground">
                                    <input
                                        type="radio"
                                        name="gender"
                                        value="female"
                                        checked={form.gender === "female"}
                                        onChange={(e) => handleChange("gender", e.target.value)}
                                        className="accent-[#0DCCF2]"
                                    />
                                    Female
                                </label>
                            </div>
                        </div>
                    </div>

                    <div className="mt-6 flex items-center justify-end gap-x-4">
                        <button type="submit" className="flex items-center gap-2 rounded-xl bg-buttonBackground shadow-xl px-6 py-2 text-sm font-semibold text-logoColor focus:outline-none">
                            <Save className="h-4 w-4" /> Save
                        </button>
                        <button type="button" className="rounded-xl px-4 py-1 text-sm font-semibold border-1 border-logoColor text-foreground focus:outline-none focus:ring-2 focus:ring-logoColor focus:ring-offset-0 hover:outline-none hover:ring-2 hover:ring-[#0DCCF2] hover:ring-offset-0">Cancel</button>

                    </div>
                </div>
            </form>
        </div>
    )
}