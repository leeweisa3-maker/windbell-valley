import Foundation
import AVFoundation
struct Note: Decodable {let track:Int;let note:Int;let start:Double;let duration:Double;let velocity:Int}
struct Score: Decodable {let duration:Double;let programs:[Int];let notes:[Note]}
struct Event {let sample:Int64;let track:Int;let note:Int;let velocity:Int;let on:Bool}
let scoreURL=URL(fileURLWithPath:CommandLine.arguments[1]),outURL=URL(fileURLWithPath:CommandLine.arguments[2])
let score=try JSONDecoder().decode(Score.self,from:Data(contentsOf:scoreURL))
let rate=48000.0,format=AVAudioFormat(standardFormatWithSampleRate:48000,channels:2)!
let engine=AVAudioEngine();var samplers:[AVAudioUnitSampler]=[]
let mix=AVAudioMixerNode();engine.attach(mix)
let reverb=AVAudioUnitReverb();engine.attach(reverb);reverb.loadFactoryPreset(.mediumHall);reverb.wetDryMix=12
engine.connect(mix,to:reverb,format:format)
engine.connect(reverb,to:engine.mainMixerNode,format:format)
for p in score.programs {let s=AVAudioUnitSampler();engine.attach(s);try s.loadSoundBankInstrument(at:URL(fileURLWithPath:"/System/Library/Components/CoreAudio.component/Contents/Resources/gs_instruments.dls"),program:UInt8(p),bankMSB:121,bankLSB:0);engine.connect(s,to:mix,format:format);samplers.append(s)}
engine.mainMixerNode.outputVolume=0.65
try engine.enableManualRenderingMode(.offline,format:format,maximumFrameCount:512)
try engine.start()
let file=try AVAudioFile(forWriting:outURL,settings:format.settings)
let buffer=AVAudioPCMBuffer(pcmFormat:engine.manualRenderingFormat,frameCapacity:512)!
var events:[Event]=[]
for n in score.notes {events.append(Event(sample:Int64(n.start*rate),track:n.track,note:n.note,velocity:n.velocity,on:true));events.append(Event(sample:Int64((n.start+n.duration)*rate),track:n.track,note:n.note,velocity:0,on:false))}
events.sort {$0.sample < $1.sample};var ix=0;let end=Int64(score.duration*rate);var stalled=0
while engine.manualRenderingSampleTime < end {
 let pos=engine.manualRenderingSampleTime
 while ix<events.count && events[ix].sample<=pos {let e=events[ix];if e.on {samplers[e.track].startNote(UInt8(e.note),withVelocity:UInt8(e.velocity),onChannel:0)}else{samplers[e.track].stopNote(UInt8(e.note),onChannel:0)};ix+=1}
 let next=ix<events.count ? min(end,events[ix].sample) : end
 let count=AVAudioFrameCount(min(512,max(1,next-pos)))
 switch try engine.renderOffline(count,to:buffer) {
 case .success: try file.write(from:buffer);stalled=0
 case .cannotDoInCurrentContext,.insufficientDataFromInputNode:stalled+=1;if stalled>100 {fatalError("Offline render stalled")}
 case .error:fatalError("Offline render failed")
 @unknown default:fatalError("Unknown renderer status")
 }
}
engine.stop();print("Rendered original acoustic soundtrack: \(score.duration)s, stereo 48 kHz")
